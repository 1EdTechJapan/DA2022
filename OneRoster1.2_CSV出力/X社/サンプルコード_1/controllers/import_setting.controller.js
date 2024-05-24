import { db } from "../models/index.js";
import moment from "moment";
import lang from "../i18n.js";
import { checkIfDuplicateExists } from "../helpers/utility.js";


let importMachingCondition, Op = false;
let currMunicipalDB = false;

/**
 * Setting db connection to selected municipal
 * @constructor 
 */
const initMunicipalDb = (municipalId) => {
  if (municipalId) {
    if (currMunicipalDB != municipalId) {
      currMunicipalDB = municipalId;
      importMachingCondition = db[municipalId].settingMatchingConditionModel;
      Op = db[municipalId].Sequelize.Op;
    }
  }else{
    console.log("INIT MUNICIPAL NULL import_setting.controller ", municipalId);
  }
};

/**
 * Get user matching setting
 * @constructor
 */
export const findMatchingCondition = async (req, res) => {
  try {
    let municipalId = req.params.id;
    let type = req.query.type;

    initMunicipalDb(municipalId);

    let condition = {};
    if (municipalId && municipalId !== "undefined") condition.municipalId = { [Op.eq]: municipalId };
    if (type && type !== "undefined") condition.type = { [Op.eq]: type };

    var data = await importMachingCondition.findOne({ where: condition });

    if(data == null){
       data = {
          "municipalId":municipalId,
          "priority":"EMAIL,NAME,ATTENDANCE_NUMBER",
          "flowOption":2
       }
    }

    res.status(200).json({ status: true, data: data ? data : {} });
  } catch (error) {
    res.status(500).json({ error: error?.message });
  }
};

/**
 * Save user matching setting
 * @constructor
 */
export const saveMatchingCondition = async (req, res) => {
  try {
    const data = req.body;
    var priority = data?.priority;
    if(priority.length < 2){
      return res
        .status(500)
        .json({message : lang.t("import_setting.message.failed_none")});
    }

    var arr_priority = priority.split(",");
    var check_duplicate = checkIfDuplicateExists(arr_priority);
    if(check_duplicate.length > 0){
      return res
        .status(500)
        .json({message : lang.t("import_setting.message.failed_duplicate").replace("%s",lang.t("import_setting.label."+check_duplicate[0]))});
    }
    initMunicipalDb(data?.municipalId);
    const payloadData = {
      municipalId: data?.municipalId,
      priority: priority,
      flowOption: data?.flowOption
    };
    await importMachingCondition.upsert(payloadData);

    res.status(200).json({ status: true});
  } catch (error) {
    res.status(500).json({ error: error?.message });
  }
};
