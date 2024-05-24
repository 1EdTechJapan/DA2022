OneRoster連携

■ 環境
NodeJS : 16.19.1 
ExpressJS : v4.17.1

■ 使用ライブラリ（OneRoster連携のために必須のもの）
・bull 4.1.0
・sequelize 6.9.0
・csv-parser 3.3.0
・zip-a-folder 1.1.0
・json2csv 5.0.6
・azure/storage-blob 12.8.0
・joi/date 2.1.0
・axios 0.24.0

■ 各ディレクトリとファイルについて

|- controllers
|  |- import.controller.js : API's purpose for importing process
|  |- import_setting.controller.js : API's purpose for import setting
|  |- scheduler.controller.js : API's purpose for exporting process
|- helpers
|  |- import.js : csv reader utility
|  |- importValidation.js : csv validator utility
|  |- wtirecsv.js : csv writer utility
|- job
|  |- process
|  |  |- ImportQueueProcess.js : Process importing OneRoster ZIP to application
|  |  |- SchedulerQueueProcess.js : Process exporting OneRoster ZIP to BLOB Storage/PC
|  |  |- SubmitAdminTeacherProcess.js : Administrator matching & merging function during import process
|  |  |- SubmitClassesProcess.js : Classes matching & merging function during import process
|  |  |- SubmitGroupProcess.js : Group matching & merging function during import process
|  |  |- SubmitStudentProcess.js : Student matching & merging function during import process
|  |  |- SubmitToLgateProcess.js : Process sent imported data to L-Gate
|  |  |- SubmitUsersEnrollmentsGroupProcess.js : Group enrollment matching & merging function during import process
|  |  |- SubmitUsersEnrollmentsProcess.js : Class enrollment matching & merging function during import process
|  |  |- SubmitUsersTeacherProcess.js : Teacher matching & merging function during import process
| README : 本ファイル


