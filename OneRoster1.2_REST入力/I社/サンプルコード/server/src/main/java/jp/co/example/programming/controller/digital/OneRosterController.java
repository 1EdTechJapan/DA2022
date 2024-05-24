package jp.co.example.programming.controller.digital;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import jp.co.example.programming.service.oneRoster.OrgService;
import jp.co.example.programming.service.oneRoster.RoomService;
import jp.co.example.programming.service.oneRoster.UserService;

/**
 * OneRoster REST実行コントローラー
 */
@Controller
@RequestMapping("/programming/oneRoster")
public class OneRosterController {

    @Autowired
    private OrgService orgService;

    @Autowired
    private RoomService roomService;

    @Autowired
    private UserService userService;

    /**
     * 全組織情報取得
     */
    @GetMapping("/orgs")
    public ResponseEntity<Void> getAllOrgs() {
        orgService.getAllOrgs();
        return new ResponseEntity<>(HttpStatus.OK);
    }

    /**
     * 全クラス情報取得
     */
    @GetMapping("/classes")
    public ResponseEntity<Void> getAllClasses() {
        roomService.getAllClasses();
        return new ResponseEntity<>(HttpStatus.OK);
    }

    /**
     * 全ユーザー情報取得
     */
    @GetMapping("/users")
    public ResponseEntity<Void> getAllUsers() {
        userService.getAllUsers();
        return new ResponseEntity<>(HttpStatus.OK);
    }




}
