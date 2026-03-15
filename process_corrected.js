const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

/**
 * 手机号验证（保持原来的）
 */
function validatePhone(phone) {
    if (typeof phone !== 'string') {
        phone = String(phone || '');
    }
    
    const cleaned = phone.replace(/\D/g, '');
    
    if (cleaned.length !== 11 || !cleaned.startsWith('1')) {
        return { cleaned: cleaned, valid: false, reason: '格式错误: 不是11位或不是1开头' };
    }
    
    const prefix = cleaned.substring(0, 3);
    const validPrefixes = [
        '134','135','136','137','138','139','150','151','152','157','158','159',
        '178','182','183','184','187','188','198','130','131','132','155','156',
        '166','175','176','185','186','133','153','173','177','180','181','189',
        '199','170','171'
    ];
    
    if (!validPrefixes.includes(prefix)) {
        return { cleaned: cleaned, valid: false, reason: '号段无效: 不属于已知运营商' };
    }
    
    return { cleaned: cleaned, valid: true, reason: '格式和号段有效' };
}

/**
 * 从单位名称判断是否在湖南
 */
function isCompanyInHunan(companyName) {
    if (!companyName || typeof companyName !== 'string') {
        return { valid: false, reason: '单位名称为空或不是字符串' };
    }
    
    const hunanKeywords = ['湖南', '湘', 'Hunan'];
    
    // 检查是否包含湖南关键词
    const containsKeyword = hunanKeywords.some(keyword => companyName.includes(keyword));
    
    if (!containsKeyword) {
        return { valid: false, reason: '单位名称不包含"湖南"或相关关键词' };
    }
    
    // 检查是否为有效单位（不是测试或无效名称）
    const invalidPatterns = ['测试', 'demo', '示例', 'test', '空', '无', '不详'];
    for (const pattern of invalidPatterns) {
        if (companyName.includes(pattern)) {
            return { valid: false, reason: `单位名称包含无效关键词: "${pattern}"` };
        }
    }
    
    return { valid: true, reason: '单位名称包含湖南关键词' };
}

/**
 * 主处理函数
 */
async function processCorrected() {
    const inputFile = '/Users/dadaguaijiangjun/Desktop/5000.xlsx';
    const outputFile = '/Users/dadaguaijiangjun/Desktop/5000_corrected_cleaned.csv';
    
    console.log('='.repeat(50));
    console.log('🔍 修正版数据清洗');
    console.log('='.repeat(50));
    console.log('处理逻辑:');
    console.log('  1. 手机号格式+号段验证');
    console.log('  2. 从单位名称判断是否在湖南');
    console.log('  3. 输出正确验证结果');
    console.log('='.repeat(50));
    
    try {
        // 读取Excel
        const workbook = XLSX.readFile(inputFile);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        
        console.log(`总数据行数: ${data.length}`);
        
        // 定义列名
        const headers = ['phone', 'name', 'id_card', 'company', 'amount', 'col5', 'col6', 'col7', 'province', 'city'];
        const outputHeaders = [...headers, 'phone_status', 'company_status', 'phone_reason', 'company_reason', 'final_status'];
        
        const outputRows = [];
        let totalRows = 0;
        let phoneValidCount = 0;
        let companyValidCount = 0;
        let bothValidCount = 0;
        
        // 处理每一行
        for (let i = 0; i < data.length; i++) {
            totalRows++;
            const row = data[i];
            
            if (row.length < 10) continue;
            
            // 验证手机号
            const phoneResult = validatePhone(row[0]);
            
            // 验证单位名称（第4列是单位名称）
            const companyResult = isCompanyInHunan(row[3]);
            
            // 统计
            if (phoneResult.valid) phoneValidCount++;
            if (companyResult.valid) companyValidCount++;
            if (phoneResult.valid && companyResult.valid) bothValidCount++;
            
            // 创建输出行
            const outputRow = {};
            
            // 原始数据
            for (let j = 0; j < headers.length; j++) {
                if (j === 0) {
                    outputRow[headers[j]] = phoneResult.cleaned;
                } else {
                    outputRow[headers[j]] = row[j] !== undefined ? row[j] : '';
                }
            }
            
            // 验证结果
            outputRow['phone_status'] = phoneResult.valid ? '有效' : '无效';
            outputRow['company_status'] = companyResult.valid ? '在湖南' : '不在湖南或无效';
            outputRow['phone_reason'] = phoneResult.reason;
            outputRow['company_reason'] = companyResult.reason;
            outputRow['final_status'] = (phoneResult.valid && companyResult.valid) ? '完全有效' : '无效';
            
            outputRows.push(outputRow);
            
            if (totalRows % 1000 === 0) {
                console.log(`已处理 ${totalRows} 行...`);
            }
        }
        
        console.log('\n📊 处理完成:');
        console.log(`总行数: ${totalRows}`);
        console.log(`手机号有效: ${phoneValidCount} (${(phoneValidCount/totalRows*100).toFixed(2)}%)`);
        console.log(`单位在湖南: ${companyValidCount} (${(companyValidCount/totalRows*100).toFixed(2)}%)`);
        console.log(`完全有效: ${bothValidCount} (${(bothValidCount/totalRows*100).toFixed(2)}%)`);
        
        // 写入CSV
        const csvWriter = createCsvWriter({
            path: outputFile,
            header: outputHeaders.map(col => ({ id: col, title: col }))
        });
        
        await csvWriter.writeRecords(outputRows);
        console.log(`\n✅ 修正版数据已保存到: ${outputFile}`);
        
        // 生成详细报告
        generateDetailedReport(outputRows, outputFile.replace('.csv', '_report.txt'));
        
        return {
            total: totalRows,
            phoneValid: phoneValidCount,
            companyValid: companyValidCount,
            bothValid: bothValidCount,
            outputFile: outputFile
        };
        
    } catch (error) {
        console.error('处理失败:', error.message);
        throw error;
    }
}

/**
 * 生成详细报告
 */
function generateDetailedReport(data, reportPath) {
    const total = data.length;
    const fullyValid = data.filter(row => row.final_status === '完全有效').length;
    const phoneInvalid = data.filter(row => row.phone_status === '无效').length;
    const companyInvalid = data.filter(row => row.company_status === '不在湖南或无效').length;
    
    // 收集无效原因
    const phoneReasons = {};
    const companyReasons = {};
    
    data.forEach(row => {
        if (row.phone_status === '无效') {
            phoneReasons[row.phone_reason] = (phoneReasons[row.phone_reason] || 0) + 1;
        }
        if (row.company_status === '不在湖南或无效') {
            companyReasons[row.company_reason] = (companyReasons[row.company_reason] || 0) + 1;
        }
    });
    
    let report = '='.repeat(50) + '\n';
    report += '修正版数据验证报告\n';
    report += '(基于单位名称判断是否在湖南)\n';
    report += '='.repeat(50) + '\n\n';
    
    report += `📈 总体统计:\n`;
    report += `   总记录数: ${total}\n`;
    report += `   完全有效记录: ${fullyValid} (${(fullyValid/total*100).toFixed(1)}%)\n`;
    report += `   无效记录: ${total - fullyValid} (${((total-fullyValid)/total*100).toFixed(1)}%)\n\n`;
    
    report += `📱 手机号验证:\n`;
    report += `   有效: ${total - phoneInvalid} (${((total-phoneInvalid)/total*100).toFixed(1)}%)\n`;
    report += `   无效: ${phoneInvalid} (${(phoneInvalid/total*100).toFixed(1)}%)\n\n`;
    
    report += `🏢 单位所在地验证:\n`;
    report += `   在湖南: ${total - companyInvalid} (${((total-companyInvalid)/total*100).toFixed(1)}%)\n`;
    report += `   不在湖南或无效: ${companyInvalid} (${(companyInvalid/total*100).toFixed(1)}%)\n\n`;
    
    if (Object.keys(phoneReasons).length > 0) {
        report += `⚠️ 手机号无效原因:\n`;
        Object.entries(phoneReasons).forEach(([reason, count]) => {
            report += `   ${reason}: ${count} 次 (${(count/total*100).toFixed(1)}%)\n`;
        });
        report += '\n';
    }
    
    if (Object.keys(companyReasons).length > 0) {
        report += `⚠️ 单位无效原因:\n`;
        Object.entries(companyReasons).forEach(([reason, count]) => {
            report += `   ${reason}: ${count} 次 (${(count/total*100).toFixed(1)}%)\n`;
        });
        report += '\n';
    }
    
    // 显示一些有效单位示例
    const validCompanies = data
        .filter(row => row.company_status === '在湖南')
        .map(row => row.company)
        .slice(0, 10);
    
    if (validCompanies.length > 0) {
        report += `🏭 有效单位示例（前10个）:\n`;
        validCompanies.forEach((company, idx) => {
            report += `   ${idx+1}. ${company}\n`;
        });
        report += '\n';
    }
    
    // 显示无效单位示例
    const invalidCompanies = data
        .filter(row => row.company_status === '不在湖南或无效' && row.company)
        .map(row => row.company)
        .slice(0, 10);
    
    if (invalidCompanies.length > 0) {
        report += `❌ 无效单位示例（前10个）:\n`;
        invalidCompanies.forEach((company, idx) => {
            report += `   ${idx+1}. ${company}\n`;
        });
        report += '\n';
    }
    
    report += `💡 结论:\n`;
    if (fullyValid > 0) {
        report += `   找到 ${fullyValid} 个有效客户（手机号正确且在湖南）\n`;
    } else {
        report += `   未找到完全有效的客户记录\n`;
    }
    
    report += `\n⏰ 报告生成时间: ${new Date().toLocaleString()}\n`;
    report += '='.repeat(50);
    
    fs.writeFileSync(reportPath, report, 'utf8');
    console.log(`📋 详细报告已生成: ${reportPath}`);
}

// 运行
async function main() {
    try {
        const result = await processCorrected();
        console.log('\n✅ 修正版处理完成！');
        console.log(`📁 结果文件: ${result.outputFile}`);
        console.log(`📋 详细报告: ${result.outputFile.replace('.csv', '_report.txt')}`);
        console.log(`⏰ 处理时间: ${new Date().toLocaleString()}`);
    } catch (error) {
        console.error('❌ 处理失败:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { processCorrected };