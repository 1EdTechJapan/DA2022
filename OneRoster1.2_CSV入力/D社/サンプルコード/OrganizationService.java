public class OrganizationService {
    private static final Pattern jaSchoolCode = Pattern.compile("[A-Z]\\d{12}");
    private static final Pattern jaBoardOfEducationCode = Pattern.compile("\\d{6}");

    /**
     * Parse and validate a OneRoster organizations file, and save the organizations
     *
     * @param partnerId
     * @param orgsFile
     * @return A map of organization sourcedIds to Your Company organization ids, and a set of the sourcedIds of only district organizations
     * @throws IOException
     */
    @Transactional
    public Pair<Map<String, Integer>, Set<String>> processOneRosterOrganizations(int partnerId, File orgsFile) throws IOException {
        try (CSVParser parser = CSVParser.parse(new FileReader(orgsFile), CSVFormat.RFC4180.builder().setHeader().build());) {
            oneRosterUtilService.validateHeaderValues(parser, "orgs.csv", "sourcedId", "status", "dateLastModified", "name", "type", "identifier", "parentSourcedId");
            Map<String, Integer> idsMap = new HashMap<>();
            List<dbOrganizationEntity> existingEntities = organizationDao.getForPartnerWithPartnerId(partnerId);
            Map<String, dbOrganizationEntity> entityMap = existingEntities.stream().collect(Collectors.toMap(dbOrganizationEntity::getPartnerOrganizationID, e -> e));
            Set<String> districtOrgIds = new HashSet<>();
            for (CSVRecord org : parser) {
                String sourcedId = org.get("sourcedId");
                String name = org.get("name");
                String type = org.get("type");
                String identifier = org.get("identifier");
                String parentSourcedId = org.get("parentSourcedId");
                if (StringUtil.anyEmptyOrNull(sourcedId, name, type)) {
                    throw new HttpNotAllowedException("Missing required data in orgs.csv");
                }
                if (StringUtil.containsHalfWidthKana(name)) {
                    throw new HttpNotAllowedException("Half-width katakana in orgs.csv");
                }
                oneRosterUtilService.validateStatusAndUpdateDate(parser, org, "orgs.csv");
                StringUtil.validateUUIDs(sourcedId);
                if (!type.equals("district") && !type.equals("school")) {
                    throw new HttpNotAllowedException("Invalid organization type " + type);
                } else if (type.equals("district")) {
                    if (!StringUtils.isNullOrEmpty(parentSourcedId)) {
                        throw new HttpNotAllowedException("parentSourcedId not blank for district organization");
                    }
                    validateDistrictCode(identifier);
                    districtOrgIds.add(sourcedId);
                } else {
                    //Must be school
                    validateSchoolCode(identifier);
                }
                dbOrganizationEntity orgEntity = entityMap.get(sourcedId);
                if (orgEntity == null) {
                    Organization o = OrganizationFactory.create(name, false, partnerId, sourcedId);
                    idsMap.put(sourcedId, o.getOrganizationID());
                } else {
                    if (!orgEntity.getName().equals(name) || !orgEntity.getActive()) {
                        orgEntity.setName(name);
                        orgEntity.setActive(true);
                        organizationDao.save(orgEntity);
                    }
                    idsMap.put(sourcedId, orgEntity.getOrganizationId());
                }
            }
            for (dbOrganizationEntity cur : existingEntities) {
                if (!idsMap.containsKey(cur.getPartnerOrganizationID()) && cur.getActive()) {
                    cur.setActive(false);
                    organizationDao.save(cur);
                }
            }
            return new Pair<>(idsMap, districtOrgIds);
        }
    }

    private void validateSchoolCode(String code) {
        if (StringUtils.isNullOrEmpty(code)) {
            return;
        }
        //We don't know exactly how these work, but they're all an uppercase letter followed by 12 digits,to be updated with new and correct validations
        if (!jaSchoolCode.matcher(code).matches()) {
            throw new HttpNotAllowedException("Illegal school code " + code);
        }
    }

    private void validateDistrictCode(String code) {
        if (StringUtils.isNullOrEmpty(code)) {
            return;
        }
        //We don't know exactly how these work, but they're all 6 digit numbers, to be updated with new and correct validations
        if (!jaBoardOfEducationCode.matcher(code).matches()) {
            throw new HttpNotAllowedException("Illegal district code " + code);
        }
    }
}
