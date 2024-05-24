package jp.co.example.osarai2.controller.user;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import jp.co.example.osarai2.service.user.StudyLogService;


@Controller
@RequestMapping("/osarai")
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
