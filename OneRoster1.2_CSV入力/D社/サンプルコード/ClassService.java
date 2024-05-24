public class ClassService {
    /**
     * Parse a OneRoster classes file and save the classes in the database
     *
     * @param csvFile          The CSV file to parse
     * @param courseToOrgIdMap A map of course sourcedIds to the parent organization ids in our database
     * @param districtOrgIds   The sourcedIds of all the district organizations from this roster
     * @param partnerId        The partner to associate the classes with
     * @return A map of class sourcedIds to class ids in your database
     * @throws IOException
     */
    @Transactional
    public Map<String, Integer> processOneRosterClasses(File csvFile, Map<String, Integer> courseToOrgIdMap, Set<String> districtOrgIds, int partnerId) throws IOException {
        Map<String, Integer> ids = new HashMap<>();
        try (CSVParser parser = CSVParser.parse(new FileReader(csvFile), CSVFormat.RFC4180.builder().setHeader().build())) {
            oneRosterUtilService.validateHeaderValues(parser, "classes.csv", "sourcedId", "status", "dateLastModified", "title", "grades", "courseSourcedId", "classCode", "classType", "location", "schoolSourcedId", "termSourcedIds", "subjects", "subjectCodes", "periods", "metadata.jp.specialNeeds");
            List<dbClazzEntity> entities = classDao.getForPartnerWithClassId(partnerId);
            Map<String, dbClazzEntity> entityMap = entities.stream().collect(Collectors.toMap(dbClazzEntity::getPartnerClassID, e -> e));
            for (CSVRecord classRecord : parser) {
                String sourcedId = classRecord.get("sourcedId");
                String title = classRecord.get("title");
                String courseSourcedId = classRecord.get("courseSourcedId");
                String termSourcedId = classRecord.get("termSourcedIds");
                String schoolSourcedId = classRecord.get("schoolSourcedId");
                String location = classRecord.get("location");
                String specialNeeds = classRecord.get("metadata.jp.specialNeeds");
                String classType = classRecord.get("classType");
                String grades = classRecord.get("grades");
                String subjects = classRecord.get("subjects");
                String subjectCodes = classRecord.get("subjectCodes");
                if (StringUtil.anyEmptyOrNull(sourcedId, title, courseSourcedId, termSourcedId, schoolSourcedId)) {
                    throw new HttpNotAllowedException("Missing required data in classes.csv");
                }
                oneRosterUtilService.validateStatusAndUpdateDate(parser, classRecord, "classes.csv");
                StringUtil.validateUUIDs(sourcedId, courseSourcedId, schoolSourcedId);
                StringUtil.validateUUIDs(termSourcedId.split(","));
                if (StringUtil.anyContainHalfWidthKana(title, location)) {
                    throw new HttpNotAllowedException("Half-width katakana in classes.csv");
                }
                int subjectCount = subjects == null || subjects.isEmpty() ? 0 : subjects.split(",").length;
                int subjectCodeCount = subjectCodes == null || subjectCodes.isEmpty() ? 0 : subjectCodes.split(",").length;
                if (subjectCount != subjectCodeCount) {
                    throw new HttpNotAllowedException("Invalid subjects/subjectCodes in classes.csv");
                }
                if (districtOrgIds.contains(schoolSourcedId)) {
                    throw new HttpNotAllowedException("schoolSourcedId must not be the id of a district");
                }
                Integer orgId = courseToOrgIdMap.get(courseSourcedId);
                if (orgId == null) {
                    throw new HttpNotAllowedException("Could not find organization for courseId " + courseSourcedId);
                }
                if (specialNeeds != null && !specialNeeds.isEmpty() && !specialNeeds.equalsIgnoreCase("true") && !specialNeeds.equalsIgnoreCase("false")) {
                    throw new HttpNotAllowedException("Invalid specialNeeds value " + specialNeeds);
                }
                if (classType.isEmpty() || (!classType.equals("homeroom") && !classType.equals("scheduled"))) {
                    throw new HttpNotAllowedException("Invalid classType value " + classType);
                }
                oneRosterUtilService.validateGrades(grades);
                oneRosterUtilService.validateSubjectCodes(subjectCodes);
                dbClazzEntity existing = entityMap.get(sourcedId);
                if (existing == null) {
                    dbClazzEntity created = new dbClazzEntity();
                    created.setClassName(title);
                    created.setActive(true);
                    created.setPartnerId(partnerId);
                    created.setPartnerClassID(sourcedId);
                    created.setOrganizationId(orgId);
                    // Initialize default values for new class
		    // ...
                    created.setDateCreated(new Date());
                    created.setDateModified(new Date());
                    classDao.save(created);
                    ids.put(sourcedId, created.getClassId());
                } else {
                    if (!existing.getClassName().equals(title) || !existing.getActive() | !Objects.equals(orgId, existing.getOrganizationId())) {
                        existing.setActive(true);
                        existing.setClassName(title);
                        existing.setOrganizationId(orgId);
                        existing.setDateModified(new Date());
                        classDao.save(existing);
                    }
                    ids.put(sourcedId, existing.getClassId());
                }
            }
            for (dbClazzEntity clazz : entities) {
                if (!ids.containsKey(clazz.getPartnerClassID()) && clazz.getActive()) {
                    deleteVerified(clazz.getClassId());
                }
            }
            return ids;
        }
    }

    /**
     * Parse a OneRoster class enrollments file and add accounts to classes as specified
     *
     * @param visitor     Your Company credentials to authenticate the operations
     * @param csvFile     The enrollments file
     * @param classIdMap  A map of class sourcedIds to our class ids
     * @param userIdMap   A map of user sourcedIds to our account ids
     * @param schoolIdMap A map of school sourcedIds to our organization ids
     * @param districtIds A map of district sourcedIds to our organization ids
     * @throws IOException
     */
    @Transactional
    public void processOneRosterEnrollments(Visitor visitor, File csvFile, Map<String, Integer> classIdMap, Map<String, Integer> userIdMap, Map<String, Integer> schoolIdMap, Set<String> districtIds) throws IOException {
        try (CSVParser parser = CSVParser.parse(new FileReader(csvFile), CSVFormat.RFC4180.builder().setHeader().build())) {
            oneRosterUtilService.validateHeaderValues(parser, "enrollments", "sourcedId", "status", "dateLastModified", "classSourcedId", "schoolSourcedId",
                    "userSourcedId", "role", "primary", "beginDate", "endDate", "metadata.jp.ShussekiNo", "metadata.jp.PublicFlg");
            Map<Integer, Set<Integer>> studentListMap = new HashMap<>();
            Map<Integer, Set<Integer>> teacherListMap = new HashMap<>();
            for (CSVRecord record : parser) {
                String sourcedId = record.get("sourcedId");
                String classSourcedId = record.get("classSourcedId");
                String userSourcedId = record.get("userSourcedId");
                String schoolSourcedId = record.get("schoolSourcedId");
                String role = record.get("role"); //student, teacher, administrator, or proctor
                String primary = record.get("primary");
                String beginDate = record.get("beginDate");
                String endDate = record.get("endDate");
                if (StringUtil.anyEmptyOrNull(sourcedId, classSourcedId, userSourcedId, schoolSourcedId, role, primary)) {
                    throw new HttpNotAllowedException("Missing required data from enrollments.csv");
                }
                StringUtil.validateUUIDs(sourcedId, classSourcedId, userSourcedId);
                oneRosterUtilService.validateStatusAndUpdateDate(parser, record, "enrollments.csv");
                Integer classId = classIdMap.get(classSourcedId);
                if (classId == null) {
                    throw new HttpNotAllowedException("No class found for id " + classSourcedId);
                }
                Integer accountId = userIdMap.get(userSourcedId);
                if (accountId == null) {
                    throw new HttpNotAllowedException("No user found for id " + userSourcedId);
                }
                if (!schoolIdMap.containsKey(schoolSourcedId)) {
                    throw new HttpNotAllowedException("No organization found for id " + schoolSourcedId);
                }
                if (districtIds.contains(schoolSourcedId)) {
                    throw new HttpNotAllowedException("District organization id not valid for schoolSourcedId");
                }
                if (beginDate != null && !beginDate.isEmpty()) {
                    oneRosterUtilService.validateDateFormat(beginDate, "enrollments.csv", "beginDate");
                }
                if (endDate != null && !endDate.isEmpty()) {
                    oneRosterUtilService.validateDateFormat(endDate, "enrollments.csv", "endDate");
                }

                Set<Integer> students = studentListMap.get(classId);
                Set<Integer> teachers = teacherListMap.get(classId);
                if (students == null) {
                    students = new HashSet<>();
                    teachers = new HashSet<>();
                    studentListMap.put(classId, students);
                    teacherListMap.put(classId, teachers);
                }
                switch (role) {
                    case "student":
                        if (!primary.equalsIgnoreCase("false")) {
                            throw new HttpNotAllowedException("primary must be false for students");
                        }
                        students.add(accountId);
                        break;
                    case "teacher":
                    case "proctor":
                    case "administrator":
                        if (!primary.equalsIgnoreCase("false") && !primary.equalsIgnoreCase("true")) {
                            throw new HttpNotAllowedException("Invalid primary value " + primary);
                        }
                        teachers.add(accountId);
                        break;
                    default:
                        throw new HttpNotAllowedException("Unrecognized enrollment role " + role);
                }
            }
            List<ClassMembershipSyncData> syncDataList = new ArrayList<>();
            for (Integer id : studentListMap.keySet()) {
                Set<Integer> students = studentListMap.get(id);
                Set<Integer> teachers = teacherListMap.get(id);
                ClassMembershipSyncData syncData = new ClassMembershipSyncData();
                syncData.setClassID(id);
                syncData.setStudentAccountIDs(new ArrayList<>(students));
                syncData.setTeacherAccountIDs(new ArrayList<>(teachers));
                syncDataList.add(syncData);
            }
            if (!CollectionUtils.isEmpty(syncDataList)) {
                syncClassMembership(visitor, syncDataList, false);
            }
        }
    }
}
