package jp.co.example.programming.service.oneRoster;

import java.util.List;

import org.springframework.stereotype.Service;

import jp.co.example.programming.openapi.controller.oneRoster.ClassesManagementApi;
import jp.co.example.programming.openapi.data.oneRoster.ClassDType;
import jp.co.example.programming.openapi.data.oneRoster.ClassSetDType;

/**
 * 教室情報操作クラス
 */
@Service
public class RoomService {

    /**
     * OneRoster RESTからClasses情報を取得し、教室情報をデータベースに登録します
     */
    public void getAllClasses() {
        ClassesManagementApi api = new ClassesManagementApi();
        ClassSetDType classSet = api.getAllClasses(null, null, null, null, null, null);
        List<ClassDType> classes = classSet.getClasses();

        // OneRoster RESTで取得したデータからデータベース登録用の教室情報Listを生成、登録
        // 自社独自領域のため、詳細割愛
    }




}
