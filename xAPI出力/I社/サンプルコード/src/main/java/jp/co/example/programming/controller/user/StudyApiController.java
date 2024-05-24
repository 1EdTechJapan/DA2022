package jp.co.example.programming.controller.user;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import jp.co.example.programming.service.user.StudyLogService;


@Controller
@RequestMapping("/programming")
public class StudyApiController {

    @Autowired
    private StudyLogService studyLogService;




    /**
     * 学習結果登録
     * 学習結果を登録します
     *
     * @param studyRequest
     * @return
     */
    @PostMapping(
        value = "/study",
        produces = { "application/json" },
        consumes = { "application/json" }
    )
    public ResponseEntity<Void> study(/* StudyRequest studyRequest */) {
        studyLogService.create(/* studyRequest */);
        return new ResponseEntity<>(HttpStatus.OK);
    }

}
