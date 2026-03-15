const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

/**
 * 验证手机号码格式
 * @param {string} phone - 手机号码
 * @returns {Object} {cleaned: 清理后的号码, valid: 是否有效}
 */
function validatePhone(phone) {
    if (typeof phone !== 'string') {
        phone = String(phone || '');
    }
    
    // 清理非数字字符
    const cleaned = phone.replace(/\D/g, '');
    
    // 验证: 11位且以1开头
    const valid = cleaned.length === 11 && cleaned.startsWith('1');
    
    return {
        cleaned: cleaned,
        valid: valid
    };
}

/**
 * 检查地址是否在湖南
 * @param {string} address - 地址
 * @returns {boolean} 是否在湖南
 */
function isHunanAddress(address) {
    if (typeof address !== 'string') {
        address = String(address || '');
    }
    
    const keywords = ['湖南', '湖南省', 'Hunan'];
    return keywords.some(keyword => address.includes(keyword));
}

/**
 * 处理CSV文件
 * @param {string} inputPath - 输入文件路径
 * @param {string} outputPath - 输出文件路径
 * @param {string} phoneColumn - 电话列名
 * @param {string} addressColumn - 地址列名
 */
async function processCsvFile(inputPath, outputPath, phoneColumn = 'phone', addressColumn = 'address') {
    console.log(`开始处理文件: ${inputPath}`);
    
    return new Promise((resolve, reject) => {
        const rows = [];
        let headers = [];
        let totalRows = 0;
        let validRows = 0;
        
        // 先读取前几行获取表头
        const readStream = fs.createReadStream(inputPath);
        const csvStream = csv();
        
        csvStream.on('headers', (headerList) => {
            headers = headerList;
            console.log(`检测到表头: ${headers.join(', ')}`);
            
            // 自动检测电话列
            let detectedPhoneCol = phoneColumn;
            if (!headers.includes(phoneColumn)) {
                const possibleCols = headers.filter(col => 
                    col.includes('电话') || col.includes('手机') || col.toLowerCase().includes('phone')
                );
                if (possibleCols.length > 0) {
                    detectedPhoneCol = possibleCols[0];
                    console.log(`自动检测到电话列: ${detectedPhoneCol}`);
                } else {
                    console.error(`未找到电话列，可用列: ${headers.join(', ')}`);
                    reject(new Error('未找到电话列'));
                    return;
                }
            }
            phoneColumn = detectedPhoneCol;
            
            // 自动检测地址列
            let detectedAddressCol = addressColumn;
            if (!headers.includes(addressColumn)) {
                const possibleCols = headers.filter(col => 
                    col.includes('地址') || col.includes('单位') || col.toLowerCase().includes('address')
                );
                if (possibleCols.length > 0) {
                    detectedAddressCol = possibleCols[0];
                    console.log(`自动检测到地址列: ${detectedAddressCol}`);
                } else {
                    console.log('警告: 未找到地址列，将跳过地址验证');
                    detectedAddressCol = null;
                }
            }
            addressColumn = detectedAddressCol;
        });
        
        csvStream.on('data', (row) => {
            totalRows++;
            
            // 验证电话
            const phoneResult = validatePhone(row[phoneColumn]);
            row[phoneColumn] = phoneResult.cleaned;
            
            // 验证地址（如果地址列存在）
            let addressValid = true;
            if (addressColumn && row[addressColumn]) {
                addressValid = isHunanAddress(row[addressColumn]);
            }
            
            // 如果电话有效且在湖南（或地址未验证），则保留
            if (phoneResult.valid && addressValid) {
                validRows++;
                rows.push(row);
            }
            
            // 每处理10000行显示进度
            if (totalRows % 10000 === 0) {
                console.log(`已处理 ${totalRows} 行，有效 ${validRows} 行`);
            }
            
            // 如果数据太多，可以分批写入文件
            if (rows.length >= 100000) {
                // 这里可以添加分批写入逻辑
            }
        });
        
        csvStream.on('end', async () => {
            console.log(`文件读取完成，总行数: ${totalRows}`);
            
            if (rows.length === 0) {
                console.log('没有有效数据');
                resolve({ total: totalRows, valid: 0 });
                return;
            }
            
            // 准备CSV写入器
            const csvWriter = createCsvWriter({
                path: outputPath,
                header: headers.map(col => ({ id: col, title: col }))
            });
            
            try {
                await csvWriter.writeRecords(rows);
                console.log(`有效数据已写入: ${outputPath}`);
                console.log(`有效行数: ${validRows} (${(validRows/totalRows*100).toFixed(2)}%)`);
                console.log(`无效行数: ${totalRows - validRows}`);
                
                resolve({
                    total: totalRows,
                    valid: validRows,
                    outputPath: outputPath
                });
            } catch (error) {
                reject(error);
            }
        });
        
        csvStream.on('error', (error) => {
            reject(error);
        });
        
        readStream.pipe(csvStream);
    });
}

/**
 * 主函数
 */
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.log('用法: node data_processor.js <输入文件> [电话列名] [地址列名]');
        console.log('示例: node data_processor.js data.csv phone address');
        process.exit(1);
    }
    
    const inputFile = args[0];
    const phoneColumn = args[1] || 'phone';
    const addressColumn = args[2] || 'address';
    
    // 检查输入文件是否存在
    if (!fs.existsSync(inputFile)) {
        console.error(`文件不存在: ${inputFile}`);
        process.exit(1);
    }
    
    // 设置输出文件路径
    const desktopDir = path.join(require('os').homedir(), 'Desktop');
    const inputName = path.basename(inputFile, path.extname(inputFile));
    const outputFile = path.join(desktopDir, `${inputName}_cleaned.csv`);
    
    console.log(`输入文件: ${inputFile}`);
    console.log(`输出文件: ${outputFile}`);
    console.log(`电话列: ${phoneColumn}`);
    console.log(`地址列: ${addressColumn}`);
    console.log('---');
    
    try {
        const result = await processCsvFile(inputFile, outputFile, phoneColumn, addressColumn);
        console.log('\n✅ 处理完成！');
        console.log(`📊 统计:`);
        console.log(`   总行数: ${result.total}`);
        console.log(`   有效行数: ${result.valid}`);
        console.log(`   输出文件: ${result.outputPath}`);
    } catch (error) {
        console.error('\n❌ 处理失败:', error.message);
        process.exit(1);
    }
}

// 运行主函数
if (require.main === module) {
    main();
}

module.exports = { processCsvFile, validatePhone, isHunanAddress };