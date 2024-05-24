package jp.co.example.osarai2.service.oneRoster;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;

import jp.co.example.osarai2.openapi.controller.oneRoster.EnrollmentsManagementApi;
import jp.co.example.osarai2.openapi.controller.oneRoster.UsersManagementApi;
import jp.co.example.osarai2.openapi.data.oneRoster.EnrollmentDType;
import jp.co.example.osarai2.openapi.data.oneRoster.EnrollmentSetDType;
import jp.co.example.osarai2.openapi.data.oneRoster.UserDType;
import jp.co.example.osarai2.openapi.data.oneRoster.UserSetDType;

/**
 * 学習者情報操作クラス
 */
@Service
public class UserService {

    /**
     * OneRosterからUsersとEnrollments情報を取得し、学習者情報をデータベースに登録します
     */
    public void getAllUsers() {
        // OneRoster UsersManagementApiからUserDType一覧を取得
        UsersManagementApi usersApi = new UsersManagementApi();
        UserSetDType userSet = usersApi.getAllUsers(null, null, null, null, null, null);
        List<UserDType> users = userSet.getUsers();

        // OneRoster EnrollmentsManagementApiからEnrollmentDType一覧を取得
        EnrollmentsManagementApi enrollmentsApi = new EnrollmentsManagementApi();
        EnrollmentSetDType enrollmentSet = enrollmentsApi.getAllEnrollments(null, null, null, null, null, null);
        List<EnrollmentDType> enrollments = enrollmentSet.getEnrollments();

        // Users.sourcedIdとClasses.sourcedIdのMapを生成
        Map<String, String> userIdClassIdMap = new HashMap<>();
        for (EnrollmentDType enrollment : enrollments) {
            String userSourcedId  = enrollment.getUser().getSourcedId();
            String classSourcedId = enrollment.getPropertyClass().getSourcedId();
            userIdClassIdMap.put(userSourcedId, classSourcedId);
        }

        // 自社独自領域のため、詳細割愛
        // OneRoster RESTで取得したデータからデータベース登録用の学習者情報Listを生成、登録
    }




}
