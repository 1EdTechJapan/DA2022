package com.group.oneroster.web.dto;


import com.opencsv.bean.CsvBindByPosition;
import lombok.AccessLevel;
import lombok.Data;
import lombok.experimental.FieldDefaults;

@Data
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserRecord {
    @CsvBindByPosition(position = 0)
    String sourcedId;
    @CsvBindByPosition(position = 1)
    String status;
    @CsvBindByPosition(position = 2)
    String dateLastModified;
    @CsvBindByPosition(position = 3)
    String enabledUser;
    @CsvBindByPosition(position = 4)
    String username;
    @CsvBindByPosition(position = 5)
    String userIds;
    @CsvBindByPosition(position = 6)
    String givenName;
    @CsvBindByPosition(position = 7)
    String familyName;
    @CsvBindByPosition(position = 8)
    String middleName;
    @CsvBindByPosition(position = 9)
    String identifier;
    @CsvBindByPosition(position = 10)
    String email;
    @CsvBindByPosition(position = 11)
    String sms;
    @CsvBindByPosition(position = 12)
    String phone;
    @CsvBindByPosition(position = 13)
    String agentSourcedIds;
    @CsvBindByPosition(position = 14)
    String grades;
    @CsvBindByPosition(position = 15)
    String password;
    @CsvBindByPosition(position = 16)
    String userMasterIdentifier;
    @CsvBindByPosition(position = 17)
    String preferredGivenName;
    @CsvBindByPosition(position = 18)
    String preferredMiddleName;
    @CsvBindByPosition(position = 19)
    String preferredFamilyName;
    @CsvBindByPosition(position = 20)
    String primaryOrgSourcedId;
    @CsvBindByPosition(position = 21)
    String pronouns;
}
