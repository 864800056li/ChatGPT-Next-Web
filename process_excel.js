const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

/**
 * 验证手机号码格式
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
 * 检查是否在湖南
 */
function isHunan(province) {
    if (typeof province !== 'string') {
        province = String(province || '');
    }
    return province.includes('湖南');
}

/**
 * 主处理函数
 */
async function processExcelFile(inputPath, outputPath) {
    console.log('开始处理Excel文件:', inputPath);
    
    try {
        // 读取工作簿
        const workbook = XLSX.readFile(inputPath);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        
        // 转换为JSON数组（没有表头）
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        
        console.log('总数据行数:', data.length);
        
        if (data.length === 0) {
            console.log('文件为空');
            return;
        }
        
        // 定义列名（根据观察）
        const headers = [
            'phone',        // 0: 电话号码
            'name',         // 1: 姓名
            'id_card',      // 2: 身份证号
            'company',      // 3: 单位名称
            'amount',       // 4: 金额
            'col5',         // 5: 未知列5
            'col6',         // 6: 未知列6
            'col7',         // 7: 未知列7
            'province',     // 8: 省份
            'city'          // 9: 城市
        ];
        
        const validRows = [];
        let totalRows = 0;
        let validCount = 0;
        
        // 处理每一行数据
        for (let i = 0; i < data.length; i++) {
            totalRows++;
            const row = data[i];
            
            // 确保行有足够列
            if (row.length < 10) {
                continue; // 跳过不完整的行
            }
            
            // 验证电话号码（第0列）
            const phoneResult = validatePhone(row[0]);
            
            // 验证省份（第8列）
            const provinceValid = isHunan(row[8]);
            
            // 如果电话有效且在湖南，保留该行
            if (phoneResult.valid && provinceValid) {
                validCount++;
                
                // 创建对象，使用清理后的电话号码
                const rowObj = {};
                for (let j = 0; j < headers.length; j++) {
                    if (j === 0) {
                        // 使用清理后的电话号码
                        rowObj[headers[j]] = phoneResult.cleaned;
                    } else {
                        rowObj[headers[j]] = row[j] !== undefined ? row[j] : '';
                    }
                }
                
                validRows.push(rowObj);
            }
            
            // 显示进度
            if (totalRows % 1000 === 0) {
                console.log(`已处理 ${totalRows} 行，有效 ${validCount} 行`);
            }
        }
        
        console.log(`\n处理完成:`);
        console.log(`总行数: ${totalRows}`);
        console.log(`有效行数: ${validCount}`);
        console.log(`无效行数: ${totalRows - validCount}`);
        
        if (validRows.length === 0) {
            console.log('没有有效数据');
            return;
        }
        
        // 准备CSV写入器
        const csvWriter = createCsvWriter({
            path: outputPath,
            header: headers.map(col => ({ id: col, title: col }))
        });
        
        // 写入数据
        await csvWriter.writeRecords(validRows);
        console.log(`\n有效数据已保存到: ${outputPath}`);
        
        // 显示一些统计信息
        console.log(`\n📊 数据统计:`);
        console.log(`   有效数据占比: ${(validCount/totalRows*100).toFixed(2)}%`);
        
        // 显示城市分布
        const cityCount = {};
        validRows.forEach(row => {
            const city = row.city || '未知';
            cityCount[city] = (cityCount[city] || 0) + 1;
        });
        
        console.log(`\n🏙️ 城市分布（前10）:`);
        const sortedCities = Object.entries(cityCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        sortedCities.forEach(([city, count]) => {
            console.log(`   ${city}: ${count} 条 (${(count/validCount*100).toFixed(1)}%)`);
        });
        
    } catch (error) {
        console.error('处理过程中出错:', error.message);
        throw error;
    }
}

/**
 * 主函数
 */
async function main() {
    const inputFile = '/Users/dadaguaijiangjun/Desktop/5000.xlsx';
    const outputDir = '/Users/dadaguaijiangjun/Desktop';
    const outputFile = path.join(outputDir, '5000_cleaned.csv');
    
    console.log('='.repeat(50));
    console.log('📁 Excel 数据清洗工具');
    console.log('='.repeat(50));
    console.log(`输入文件: ${inputFile}`);
    console.log(`输出文件: ${outputFile}`);
    console.log('处理任务:');
    console.log('  1. 验证手机号码格式（11位，1开头）');
    console.log('  2. 筛选省份为"湖南"的数据');
    console.log('  3. 生成清洗后的CSV文件');
    console.log('='.repeat(50));
    
    // 检查输入文件是否存在
    if (!fs.existsSync(inputFile)) {
        console.error(`❌ 输入文件不存在: ${inputFile}`);
        process.exit(1);
    }
    
    try {
        await processExcelFile(inputFile, outputFile);
        console.log('\n✅ 处理完成！');
        console.log(`📁 结果文件: ${outputFile}`);
        console.log(`⏰ 处理时间: ${new Date().toLocaleString()}`);
    } catch (error) {
        console.error('\n❌ 处理失败:', error.message);
        process.exit(1);
    }
}

// 运行主函数
if (require.main === module) {
    main();
}

module.exports = { processExcelFile };