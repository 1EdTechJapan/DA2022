package jp.co.example.programming.service.oneRoster;

import java.util.List;

import org.springframework.stereotype.Service;

import jp.co.example.programming.openapi.controller.oneRoster.OrgsManagementApi;
import jp.co.example.programming.openapi.data.oneRoster.OrgDType;
import jp.co.example.programming.openapi.data.oneRoster.OrgSetDType;

/**
 * 組織情報操作クラス
 */
@Service
public class OrgService {

    /**
     * OneRosterからOrgs情報を取得し、組織情報をデータベースに登録します
     */
    public void getAllOrgs() {
        // OneRoster OrgsManagementApiからOrgDType一覧を取得
        OrgsManagementApi api = new OrgsManagementApi();
        OrgSetDType orgSet = api.getAllOrgs(null, null, null, null, null, null);
        List<OrgDType> orgs = orgSet.getOrgs();

        // OneRoster RESTで取得したデータからデータベース登録用の組織情報Listを生成、登録
        // 自社独自領域のため、詳細割愛
    }




}
