public class AccountService {
    /**
     * Parse and validate a OneRoster users file and save the users in the database
     *
     * @param visitor   Your Company credentials to authenticate account creation
     * @param csvFile   The users file
     * @param partnerId The partner to associate the users with
     * @param classIds  A map of class sourcedIds to Your Company class ids
     * @param orgIds    A map of organization sourcedIds to Your Company organization ids
     * @return A map of user sourcedIds to Your Company account Ids
     * @throws IOException
     */
    @Transactional
    public Map<String, Integer> processOneRosterAccounts(Visitor visitor, File csvFile, int partnerId, Map<String, Integer> classIds, Map<String, Integer> orgIds) throws IOException {
        try (CSVParser parser = CSVParser.parse(new FileReader(csvFile), CSVFormat.RFC4180.builder().setHeader().build())) {
            oneRosterUtilService.validateHeaderValues(parser, "users.csv", "sourcedId", "status", "dateLastModified", "enabledUser", "username", "userIds", "givenName",
                    "familyName", "middleName", "identifier", "email", "sms", "phone", "agentSourcedIds", "grades", "password", "userMasterIdentifier", "resourceSourcedIds",
                    "preferredGivenName", "preferredMiddleName", "preferredFamilyName", "primaryOrgSourcedId", "pronouns", "metadata.jp.kanaGivenName",
                    "metadata.jp.kanaFamilyName", "metadata.jp.kanaMiddleName", "metadata.jp.homeClass");
            Map<String, Integer> ids = new HashMap<>();
            //Find the existing accounts associated with this partner and the ids that partner has given us for them
            List<dbAccountPartnerMatchEntity> partnerMatches = accountPartnerMatchDao.getAccountsForPartner(partnerId);
            Map<String, dbAccountPartnerMatchEntity> partnerMatchEntityMap = partnerMatches.stream().collect(Collectors.toMap(e -> e.getPartnerAccountId(), e -> e)); //Partner's ids to database entity
            Map<Integer, dbAccountPartnerMatchEntity> partnerMatchEntityMapInverse = partnerMatches.stream().collect(Collectors.toMap(e -> e.getAccountId(), e -> e)); //Our ids to database entity
            List<dbAccountSSOIdEntity> ssoIdMatches = accountSSOIdDao.getByProviderId(SSOProvider.MEXCBT.getId()); //Saved UserMasterIdentifiers
            Map<String, dbAccountSSOIdEntity> ssoIdMap = ssoIdMatches.stream().collect(Collectors.toMap(e -> e.getIdentifier(), e -> e));
            Map<Integer, dbAccountSSOIdEntity> ssoIdMapInverse = ssoIdMatches.stream().collect(Collectors.toMap(e -> e.getAccountId(), e -> e));
            Set<String> userMasterIdentifiers = new HashSet<>();
            for (CSVRecord record : parser) {
                String sourcedId = record.get("sourcedId");
                String enabledUser = record.get("enabledUser");
                String userMasterIdentifier = StringUtils.isEmpty(record.get("userMasterIdentifier")) ? null : record.get("userMasterIdentifier");
                String userName = record.get("username");
                String userIds = record.get("userIds");
                String primaryOrgId = record.get("primaryOrgSourcedId");
                String givenName = record.get("givenName");
                String familyName = record.get("familyName");
                String middleName = StringUtils.isEmpty(record.get("middleName")) ? null : record.get("middleName");
                String fullName = familyName + " " + (middleName == null ? "" : middleName + " ") + givenName;
                String preferredGivenName = record.get("preferredGivenName");
                String preferredMiddleName = record.get("preferredMiddleName");
                String preferredFamilyName = record.get("preferredFamilyName");
                String kanaGivenName = record.get("metadata.jp.kanaGivenName");
                String kanaMiddleName = record.get("metadata.jp.kanaMiddleName");
                String kanaFamilyName = record.get("metadata.jp.kanaFamilyName");
                String homeClass = record.get("metadata.jp.homeClass");
                String email = StringUtils.isEmpty(record.get("email")) ? null : record.get("email");
                String grades = record.get("grades");
                if (StringUtil.anyEmptyOrNull(sourcedId, enabledUser, userName, givenName, familyName, preferredGivenName, preferredFamilyName, kanaGivenName, kanaFamilyName, homeClass, userMasterIdentifier)) {
                    throw new HttpNotAllowedException("Missing required data in users.csv");
                }
                StringUtil.validateUUIDs(sourcedId, userMasterIdentifier);
                oneRosterUtilService.validateStatusAndUpdateDate(parser, record, "users.csv");
                if (StringUtil.anyContainHalfWidthKana(givenName, middleName, familyName, preferredFamilyName, preferredMiddleName, preferredGivenName, kanaGivenName, kanaFamilyName, kanaMiddleName)) {
                    throw new HttpNotAllowedException("Half-width katakana in users.csv");
                }
                if (!enabledUser.equalsIgnoreCase("true")) {
                    throw new HttpNotAllowedException("Invalid enabledUser value " + enabledUser);
                }
                if (userMasterIdentifier != null) {
                    if (userMasterIdentifiers.contains(userMasterIdentifier)) {
                        throw new HttpNotAllowedException("Duplicate userMasterIdentifier");
                    }
                    userMasterIdentifiers.add(userMasterIdentifier);
                }
                validateOneRosterUserIds(userIds);
                if (primaryOrgId != null && !primaryOrgId.isEmpty() && !orgIds.containsKey(primaryOrgId)) {
                    throw new HttpNotAllowedException("Unrecognized primaryOrgSourcedId");
                }
                if (!classIds.containsKey(homeClass)) {
                    throw new HttpNotAllowedException("Unrecognized homeClass");
                }
                oneRosterUtilService.validateGrades(grades);
                if (partnerMatchEntityMap.containsKey(userMasterIdentifier)) {
                    int accountId = partnerMatchEntityMap.get(sourcedId).getAccountId();
                    ids.put(sourcedId, accountId);
                    updateAccountOneRoster(accountId, partnerId, sourcedId, userMasterIdentifier, fullName, email, partnerMatchEntityMapInverse, ssoIdMapInverse);
                } else if (StringUtils.isNotEmpty(userMasterIdentifier) && ssoIdMap.containsKey(userMasterIdentifier)) {
                    int accountId = ssoIdMap.get(userMasterIdentifier).getAccountId();
                    updateAccountOneRoster(accountId, partnerId, sourcedId, userMasterIdentifier, fullName, email, partnerMatchEntityMapInverse, ssoIdMapInverse);
                    ids.put(sourcedId, accountId);
                } else {
                    Account a = AccountFactory.createNewAccount(visitor, email, null, fullName, null, null, null, null, null, null,
                            null, null, partnerId, sourcedId, partnerId, Collections.singleton(1), null, false, null,
                            true, null, new HashSet<>());
                    if (StringUtils.isNotEmpty(userMasterIdentifier)) {
                        dbAccountSSOIdEntity ssoIdEntity = new dbAccountSSOIdEntity();
                        ssoIdEntity.setAccountId(a.accountID);
                        ssoIdEntity.setIdentifier(userMasterIdentifier);
                        ssoIdEntity.setProviderId(SSOProvider.MEXCBT.getId());
                        accountSSOIdDao.save(ssoIdEntity);
                        bridgeInfoMessageService.produceAccountAffiliationMessage(new AffiliationInfoCollection(Arrays.asList(new AffiliationInfo(
                                a.accountID, UserAffiliationType.SSO.getId(), SSOProvider.MEXCBT.getId(), userMasterIdentifier, false
                        ))), MessageInfo.QueueMessageMode.INSERT);
                    }
                    ids.put(sourcedId, a.accountID);
                }
            }
            return ids;
        }
    }

    /**
     * Validate that a OneRoster userIds field is properly formatted
     *
     * @param userIds
     */
    private void validateOneRosterUserIds(String userIds) {
        if (userIds == null || userIds.isEmpty()) {
            return;
        }
        Pattern pattern = Pattern.compile("\\{.*:.*}");
        for (String s : userIds.split(",")) {
            if (!pattern.matcher(s).matches()) {
                throw new HttpNotAllowedException("Invalid userIds");
            }
        }
    }

    /**
     * Update an existing Your Company account to reflect data in an uploaded OneRoster users file
     *
     * @param accountId             The Your Company accountId
     * @param partnerId             The partner who uploaded the OneRoster file
     * @param sourcedId             The OneRoster sourcedId for the user
     * @param userMasterIdentifier  The OneRoster masterUserIdentifier
     * @param fullName              The user's full name from OneRoster
     * @param email                 The user's email address from OneRoster
     * @param partnerMatchEntityMap The existing partner-account matches for this partner
     * @param ssoIdMap              The existing MEXCBT userMasterIdentifiers
     */
    public void updateAccountOneRoster(int accountId, int partnerId, String sourcedId, String userMasterIdentifier, String fullName, String email,
                                       Map<Integer, dbAccountPartnerMatchEntity> partnerMatchEntityMap, Map<Integer, dbAccountSSOIdEntity> ssoIdMap) {
        if (!partnerMatchEntityMap.containsKey(accountId) || !userMasterIdentifier.equals(partnerMatchEntityMap.get(accountId).getPartnerAccountId())) {
            partnerService.addAccountPartnerMatch(accountId, partnerId, userMasterIdentifier);
        }
        if (!ssoIdMap.containsKey(accountId) && StringUtils.isNotEmpty(userMasterIdentifier)) {
            dbAccountSSOIdEntity ssoIdEntity = new dbAccountSSOIdEntity();
            ssoIdEntity.setAccountId(accountId);
            ssoIdEntity.setIdentifier(userMasterIdentifier);
            ssoIdEntity.setProviderId(SSOProvider.MEXCBT.getId());
            accountSSOIdDao.save(ssoIdEntity);
        }
        dbAccountEntity accountEntity = getAccountById(accountId);
        if (!Objects.equals(fullName, accountEntity.getName()) || !Objects.equals(email, accountEntity.getEmail())) {
            AccountFactory.updateAccount(accountId, email, null, fullName, null, null, null, null, null, null, null, null, null, null, null, null,
                    null, null, null, null, null, null, null, null, null, null, null, "OneRoster update");
        }
    }
}
