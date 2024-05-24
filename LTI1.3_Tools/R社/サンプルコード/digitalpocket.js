'use strict';

const express = require('express');
const request = require('request');
const path = require('path');
const uuid = require('uuid');

// https://github.com/Cvmcosta/ltijs
const lti = require('ltijs').Provider;

// https://github.com/examind-ai/ltijs-firestore
const { default: Firestore } = require('@examind/ltijs-firestore');

// firebaseの設定を読み込む
const serviceAccount = require('../service-account.json');


// logo画像は自動登録で必要。
lti.whitelist('/logo.png');

// dbへの暗号化のkeyを適当に決める
lti.setup('<DBSecretKey>',
    { plugin: firestore },
    {
        appRoute: '/', loginRoute: '/login',

        // クロスサイトcookiesのために以下の設定が必要
        cookies: {
            secure: true,
            sameSite: 'None'
        },

        // 開発者モードかどうか
        devMode: false,

        // 以下はLTI Dynamic Registrationに必要。Mooldeで動作確認すみ。
        dynRegRoute: '/register', // Setting up dynamic registration route. Defaults to '/register'
        dynReg: {
            url: 'https://vislti.viscuit.com', // Tool Provider URL. Required field.
            name: 'Vis LTI', // Tool Provider name. Required field.
            logo: 'https://vislti.viscuit.com/logo.png', // Tool Provider logo URL.
            description: 'Vis LTI', // Tool Provider description.
            redirectUris: [], // Additional redirection URLs. The main URL is added by default.
            customParameters: {}, // Custom parameters.
            autoActivate: true // Whether or not dynamically registered Platforms should be automatically activated. Defaults to false.
        }
    }
);

// Japan Profileのroleかどうかの判定
// rsはlist
function checkRoles(rs) {
    if (rs.length == 0) return false;
    var roles = [
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#None",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport",
        "http://purl.imsglobal.org/vocab/lis/v2/system/person#User",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#None",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer",
        "http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Member",
        "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer"];
    var i;
    for (i = 0; i < rs.length; i++) {
        var r = rs[i];
        if (!roles.includes(r)) return false;
    }
    return true;
}

// uuid v4の判定
function checkUUID(uid) {
    if (uuid.validate(uid)) {
        return (uid[14] == '4') // check UUID V4
    }
    return false;
}


// deployment id の判定
function ckechDeploymentId(did) {
    var r1 = /^S_[A-H][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$/;
    var r2 = /^[BP]_[0-9][0-9][0-9][0-9][0-9][0-9]$/;
    return r1.test(did) || r2.test(did);
}


// gradeの判定
function checkGrade(g) {
    var r = /^[PJHE][1-6]$/;
    return r.test(g);
}

// Set lti launch callback
lti.onConnect(async (token, req, res) => {

    // 認証が終わり、アプリが起動されるとここが呼び出される。
    // テストの異常系はこれ以前にエラーでここまでこない。
    // japan profileのデータフォーマット異常についてのみここではチェックする必要がある。

    let resource = req.query['res'];
    let user = token.user;

    let cid = token.clientId;
    let did = token.deploymentId;
    let pid = token.platformId;

    let targetlink = token.platformContext.targetLinkUri;

    let roles = token.platformContext.roles;

    // 以下はjapan profileで決められた仕様かどうかをチェックする部分。

    // ロールがjapan profileかどうか。
    if (!checkRoles(roles)) {
        return res.send(`<html><body><h1>invalid roles</h1> ${roles}</body></html>`);
    }

    // sub がuuid v4かどうか。
    if (!checkUUID(user)) {
        return res.send(`<html><body><h1>invalid uuid</h1> ${user}</body></html>`);
    }

    // 正しい deployment_idかどうか。
    if (!ckechDeploymentId(did)) {
        return res.send(`<html><body><h1>invalid deploymentid</h1> ${did}</body></html>`);
    }

    // ただしいcontext_idかどうか。
    let pc = token.platformContext;
    if (pc.context && pc.context.id == "") {
        return res.send(`<html><body><h1>invalid context_id</h1> ${JSON.stringify(pc.context)}</body></html>`);
    }

    // guidが空かどうかのチェック。
    let tp = token.platformInfo;
    if (tp && tp.guid == "") {
        return res.send(`<html><body><h1>invalid tool_platform/guid</h1> ${JSON.stringify(tp)}</body></html>`);
    }

    // gradeが正しいかどうか。
    if (pc.custom && !checkGrade(pc.custom.grade)) {
        return res.send(`<html><body><h1>invalid grade</h1> ${pc.custom.grade}</body></html>`);
    }


    // ここでuser のuuidから、すでにOneRosterで登録されているユーザを検索する。
    // firebaseのカスタムトークンを作成し、そのユーザとして認証し、そのトークンでアプリ本体を起動する。

    var s = "";
    s += '<html>';
    s += '<body>';
    s += '<h1>Viscuit LTI</h1>';

    // ここでは開発用にアプリ起動用のURLを表示させているが、実際にはredirectする。
    s += `<p><a href="XXXXXXXX">invoke</a></p>`;

    s += '</body></html>';
    return res.send(s);
});


// 以下は deeplink用のコード
lti.onDeepLinking((token, req, res) => {
    var dls = token.platformContext.deepLinkingSettings;
    console.log(token);
    console.log(dls);

    lti.redirect(res, '/deeplink');
});

lti.app.get('/deeplink', async (req, res) => {

    // このページでコンテンツを選択し、次のURLをpostする。
    return res.sendFile(path.join(__dirname, '/contents.html'));

    //send('deep link.');
});

lti.app.post('/deeplink', async (req, res) => {
    // このURLでpostされた情報を返すことでdeeplinkが作成される。
    var resource = req.body;
    const items = [
        {
            type: 'ltiResourceLink',
            title: resource.title,
            url: resource.url
        }
    ];
    const form = await lti.DeepLinking.createDeepLinkingForm(res.locals.token, items, { message: 'Success' });
    return res.send(form);
});

lti.app.use('/logo.png', express.static('/logo.png'));

const setup = async () => {

    // Deploy server and open connection to the database
    await lti.deploy({ port: 8888 }) // Specifying port. Defaults to 3000


    // 以下のように静的にプラットフォームを登録できる。
    // 実運用ではdynamic regstrationが簡単なので、これは使用しない。

    await lti.registerPlatform({
        url: 'https://api.ltiorc.edustd.jp/platform/XXXXXXX',
        name: 'japan ltitest',
        clientId: 'XXXXXXX',
        authenticationEndpoint: 'https://api.ltiorc.edustd.jp/platform/auth/XXXXXXX',

        // 今回のテストでは使用しないが、このURLがなければ起動しなかったため存在しないURLを記入した。
        // 実際の運用ではこのURLを与えられるので正しいURLを記入できる。
        accesstokenEndpoint: 'https://api.ltiorc.edustd.jp/platform/authXXX/XXXXXXXX',
        authConfig: { method: 'JWK_SET', key: 'https://api.ltiorc.edustd.jp/platform/jwks' }
    })

}

setup()
