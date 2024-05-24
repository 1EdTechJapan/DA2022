import { validationResult } from "express-validator";
import { db } from "../models/index.js";
import { v4 as uuidv4 } from "uuid";
import { modelName, modelAttribute } from "../models/scheduler.model.js";
import {
  modelName as modelNameNotif,
  modelAttribute as modelAttributeNotif,
} from "../models/notifications.model.js";
import { dataSerialize, responseError } from "../helpers/jsonapi.js";
import { pagination } from "../helpers/utility.js";
import {
  startSchedulerQueue,
  removeRepeatableJob,
} from "../job/queues/SchedulerQueue.js";
import {
  BlobServiceClient,
  StorageSharedKeyCredential,
  ContainerClient,
} from "@azure/storage-blob";

import {
  STATUS_COMPLETED,
  STATUS_WAITING,
  OUTPUT_OPERATION_SCHEDULE_TO_BLOB,
  OUTPUT_OPERATION_TO_BLOB_ONCE,
  OUTPUT_OPERATION_DOWNLOAD,
} from "../constants/constans.js";
import moment from "moment";
import lang from "../i18n.js";

let Municipal = db.Master.municipal;
let Scheduler, SchedulerLog, Notifications, Op = false;
let currMunicipalDB = false;

/**
 * Setting db connection to selected municipal
 * @constructor
 */
const initMunicipalDb = (municipalId) => {
  if (municipalId) {
    if (currMunicipalDB != municipalId) {
      currMunicipalDB = municipalId;
      Scheduler = db[municipalId].scheduler;
      SchedulerLog = db[municipalId].schedulerLog;
      Notifications = db[municipalId].notifications;
      Op = db[municipalId].Sequelize.Op;
    }
  }else{
    console.log("INIT MUNICIPAL NULL scheduler.controller ", municipalId);
  }
};

/**
 * Retrieve all scheduler
 * @constructor
 */
export const findAll = async (req, res) => {
  const orderby = req.query.orderby || "id";
  const sortedby = req.query.sortedby || "DESC";
  const keyword = req.query.search;
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req.query.municipal_id : req.login_user.municipal.sourcedId;

  initMunicipalDb(municipalId);

  const condition =
    keyword && keyword != "null"
      ? { title: { [Op.like]: `%${keyword}%` } }
      : null;

  const municipalCond = { municipalId: { [Op.eq]: municipalId } };

  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 20;
  const offset = page != 0 ? (page - 1) * limit : page;

  try {
    const data = await Scheduler.findAndCountAll({
      where: { ...condition, ...municipalCond },
      offset: offset,
      limit: limit,
      order: [[orderby, sortedby.toUpperCase()]],
    });
    const dataResource = dataSerialize(
      modelName,
      { ...modelAttribute, scheduler_log: {} },
      data.rows,
      pagination(data, page, limit)
    );
    res.send(dataResource);
  } catch (err) {
    responseError(
      res,
      err.message ||
        lang
          .t("scheduler.response.errorGetData")
          .replace("%DATA%", "SCHEDULERS")
    );
  }
};

/**
 * Process to create a new scheduler
 * @constructor
 */
export const store = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req.body.municipalId : req.login_user.municipal.sourcedId;
  req.body.municipalId = municipalId
  req.body.orgSourcedIds = municipalId

  initMunicipalDb(municipalId);

  const body = req.body;

  try {
    // Save
    if (body.outputOperation == "SCHEDULE_TO_BLOB") {
      body.uuid = uuidv4();
      const schedule = await Scheduler.create(body);

      const dataResource = dataSerialize(
        modelName,
        modelAttribute,
        schedule,
        null
      );
      res.send(dataResource);
    } else {
      res.send(body);
    }
  } catch (error) {
    responseError(
      res,
      error.message ||
        lang
          .t("scheduler.response.errorCreateData")
          .replace("%DATA%", "SCHEDULER")
    );
  }
};

/**
 * Process to updating a scheduler
 * @constructor
 */
export const update = async (req, res) => {
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req.body.municipalId : req.login_user.municipal.sourcedId;

  initMunicipalDb(municipalId);

  try {
    const schedule = await Scheduler.findOne({
      where: { 
        id: parseInt(req.body.id),
        municipalId : municipalId
      },
    });

    if(!schedule){
      return responseError( res, lang.t("scheduler.response.scheduleNotFound") );
    }

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    const body = req.body;
  
    removeRepeatableJob(JSON.parse(schedule.jobIds));
  
    // Save
    await Scheduler.update(body, {
      where: { id: parseInt(body.id) },
      returning: true,
    });

    const dataResource = dataSerialize(
      modelName,
      modelAttribute,
      schedule,
      null
    );

    res.send(dataResource);
  } catch (error) {
    
    responseError(
      res,
      error.message ||
        lang
          .t("scheduler.response.errorUpdateData")
          .replace("%DATA%", "SCHEDULER")
    );
  }
};

/**
 * Process to deleting a scheduler
 * @constructor
 */
export const destroy = async (req, res) => {
  const IDs = req.body.ids;
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req.body.municipal_id : req.login_user.municipal.sourcedId;
  
  initMunicipalDb(municipalId);

  const municipalCond = { municipalId: { [Op.eq]: municipalId } };

  try {
    const schedule = await Scheduler.findAll({
      attributes: ["jobIds"],
      where: { 
        id: IDs ,
        ...municipalCond
      },
    });

    
    if(schedule.length == 0){
      return responseError( res, lang.t("scheduler.response.scheduleNotFound") );
    }
  
    schedule.map((item) => {
      removeRepeatableJob(JSON.parse(item.jobIds));
    });
    await Scheduler.destroy({
      where: { id: IDs },
    });
    res.send({
      message: lang
        .t("scheduler.response.deleteSuccess")
        .replace("%DATA%", "SCHEDULER"),
    });
  } catch (error) {
    responseError(
      res,
      error.message ||
        lang
          .t("scheduler.response.deleteError")
          .replace("%DATA%", "SCHEDULER")
          .replace("%ID%", IDs)
    );
  }
};

/**
 * Get list notification of bull job of output operation
 * @constructor
 */
export const getJobNotifications = async (req, res) => {
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req?.params?.id : req.login_user.municipal.sourcedId;
  const orderby =  "createdDate";
  const sortedby = "DESC";
  const keyword = req.query.search;

  initMunicipalDb(municipalId);

  const condition =
    keyword && keyword != "null"
      ? { municipalityName: { [Op.like]: `%${keyword}%` } }
      : null;

  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 50;
  const offset = page != 0 ? (page - 1) * limit : page;

  try {
    const data = await Notifications.findAndCountAll({
      where: {
        municipalId: municipalId,
        [Op.or]: [
          {
            outputOperation: [
              OUTPUT_OPERATION_TO_BLOB_ONCE,
              OUTPUT_OPERATION_DOWNLOAD,
            ],
          },
          {
            outputOperation: OUTPUT_OPERATION_SCHEDULE_TO_BLOB,
            type : {[Op.ne] : STATUS_WAITING }
          },
        ]
      },
      offset: offset,
      limit: limit,
      order: [[orderby, sortedby.toUpperCase()]],
    });
    const dataResource = dataSerialize(
      modelNameNotif,
      modelAttributeNotif,
      data.rows,
      pagination(data, page, limit)
    );
    res.send(dataResource);
  } catch (err) {
    responseError(
      res,
      err.message ||
        lang
          .t("scheduler.response.errorGetData")
          .replace("%DATA%", "NOTIFICATIONS")
    );
  }
};

/**
 * Get list notification of bull job of output operation
 * @constructor
 */
export const getJobNotification = async (req, res) => {
  const municipalId = req?.params?.id;

  initMunicipalDb(municipalId);

  const condition =
    municipalId !== "" && municipalId !== null && municipalId !== undefined
      ? {
          municipalId: { [Op.eq]: municipalId },
        }
      : null;

  try {
    const data = await Notifications.findAll({
      attributes: [
        "id",
        "uuid",
        "municipalId",
        "jobId",
        "type",
        "userId",
        "message",
        "link",
        "outputOperation",
        "progress",
        "closed",
        "payloadRequest",
        "createdDate",
      ],
      where: condition,
      order: [
        ["createdDate", "DESC"],
        ["id", "DESC"],
      ],
    });

    const dataResource = dataSerialize(
      modelNameNotif,
      modelAttributeNotif,
      data
    );
    res.send(dataResource);
  } catch (err) {
    responseError(
      res,
      err.message ||
        lang
          .t("scheduler.response.errorGetData")
          .replace("%DATA%", "NOTIFICATIONS")
    );
  }
};

/**
 * Process to create bull job for zipping the exported data
 * @constructor
 */
export const start = async (req, res) => {
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req.body.municipalId : req.login_user.municipal.sourcedId;
  
  if(municipalId != req.body.municipalId){
    return res.status(500).send({ error: lang.t('scheduler.response.forbiden') });
  }

  initMunicipalDb(municipalId);

  try {
    let payload = {
      status: 1,
      message: lang
        .t("scheduler.response.startScheduler")
        .replace("%OUTPUT_OPERATION%", req.body.outputOperation)
        .replace("%MUNICIPAL_ID%", req.body.municipalId),
      data: {},
    };
    let notifUUID = uuidv4();

    let notifInsert = await Notifications.create({
      uuid: notifUUID,
      jobId: 0,
      municipalId: req.body.municipalId,
      type: STATUS_WAITING,
      userId: "-",
      message: lang
        .t("scheduler.response.waitingScheduler")
        .replace("%OUTPUT_OPERATION%", req.body.outputOperation)
        .replace("%SCHEDULER_NAME%", req.body.scheduleName),
      link: "",
      path: "",
      outputOperation: req.body.outputOperation,
      progress: 0,
      payloadRequest: JSON.stringify(req.body),
      createdDate: `${moment().format("YYYY-MM-DD HH:mm:ss")}`,
    });
    req.body.notifUUID = notifUUID;

    let municipalData = await Municipal.findOne({
      where: { sourcedId: req.body.municipalId },
    });

    req.body.municipalName = municipalData.municipalityName;
    let job = await startSchedulerQueue(req.body);

    payload.data = {
      job,
    };
    res.status(200).json(payload);
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
};

/**
 * Process to download zip file of exported data
 * @constructor
 */
export const download = async (req, res) => {
  const jobId = req?.params?.id;
  const municipalId = req?.params?.municipalId;

  initMunicipalDb(municipalId);

  const condition =
    jobId !== "" && jobId !== null && jobId !== undefined
      ? {
          jobId: { [Op.eq]: jobId },
          type: { [Op.eq]: STATUS_COMPLETED },
          path: { [Op.not]: null },
        }
      : null;

  try {
    const data = await Notifications.findOne({
      attributes: ["id", "jobId", "path"],
      where: condition,
    });

    const file = data?.path;
    res.download(file); // Set disposition and send it.
  } catch (err) {
    responseError(
      res,
      err.message ||
        lang
          .t("scheduler.response.errorGetData")
          .replace("%DATA%", "SCHEDULERS")
    );
  }
};

/**
 * Process to delete selected notification
 * @constructor
 */
export const closeNotif = async (req, res) => {
  const municipalId = req.login_user.municipal.sourcedId == '-' && req.login_user.role == 1 ? req.body.municipal_id : req.login_user.municipal.sourcedId;
  const obj = { closed: 1 };
  initMunicipalDb(municipalId);

  const municipalCond = { municipalId: { [Op.eq]: municipalId } };

  try {
    await Notifications.destroy({
        where: { id: { [Op.in]: req.body?.iDs} , ...municipalCond  },
      });
   
    res.send({ msg: "notif has been closed" });
    
  } catch (error) {
    responseError(
      res,
      error.message ||
        lang
          .t("scheduler.response.errorUpdateData")
          .replace("%DATA%", "NOTIFICATION")
    );
  }
};

/**
 * Process to validating BLOB url and BLOB key
 * @constructor 
 */
export const validateBlobUrl = async (req, res) => {
  const body = req.body;

  if (body.blobUrl.indexOf('blob.core.windows.net') <= -1) {
    responseError(res, lang.t("scheduler.response.errorValidateBlob"));
    return;
  }

  try {
    const blobContainerClient = new ContainerClient(
      `${body.blobUrl}${body.blobKey}`
    ); //start connection to blob use sas token

    const blockBlobClient =
      blobContainerClient.getBlockBlobClient("index.html");

    try {
      await blockBlobClient.uploadFile(`index.html`, {
        onProgress: (ev) => console.log(ev),
      });

      res.send({ status: "success", data: blockBlobClient?.url });
    } catch (err) {
      responseError(res, lang.t("scheduler.response.errorValidateBlob"));
    }
  } catch (err) {
    responseError(res, lang.t("scheduler.response.errorValidateBlob"));
  }
};
