import {existsSync,appendFileSync,mkdirSync} from 'fs';
import {Parser} from  'json2csv';

/**
 * Process to export data from table to csv files
 * @constructor
 */
const writecsv = async (fileName, folder='csv', fields, data) => {
    
    let dir = folder.split('/')
    let dirname = '';
    dir.map((item)=>{
        dirname = `${dirname}${item}/`;

        if (!existsSync(dirname)){
            mkdirSync(dirname);
        }
    })

    // output file in the same folder
    const filename = `${folder}/${fileName}`;
    let rows;
    if (!existsSync(filename)) {
        const json2csvParser = new Parser({
            fields, 
            quote: '"',
            escapedQuote: '"',
            excelStrings: false,
            header: true,
            eol : "\r\n"
        });
        rows = json2csvParser.parse(data);
    } else {
        const json2csvParser = new Parser({
            fields, 
            quote: '"',
            escapedQuote: '"',
            excelStrings: false,
            header: false,
            eol : "\r\n"
        });
        rows = json2csvParser.parse(data);
    }
    appendFileSync(filename, rows,'utf8');
    appendFileSync(filename, "\r\n", 'utf8');
}

export default writecsv