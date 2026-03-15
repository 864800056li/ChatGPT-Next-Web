const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

/**
 * 中国手机号段验证
 * 移动：134-139, 150-152, 157-159, 178, 182-184, 187-188, 198
 * 联通：130-132, 155-156, 166, 175-176, 185-186
 * 电信：133, 153, 173, 177, 180-181, 189, 199
 * 虚拟运营商：170, 171
 */
function validatePhoneEnhanced(phone) {
    if (typeof phone !== 'string') {
        phone = String(phone || '');
    }
    
    // 清理非数字字符
    const cleaned = phone.replace(/\D/g, '');
    
    // 基础验证: 11位且以1开头
    if (cleaned.length !== 11 || !cleaned.startsWith('1')) {
        return {
            cleaned: cleaned,
            valid: false,
            reason: '格式错误: 不是11位或不是1开头'
        };
    }
    
    // 提取前3位号段
    const prefix = cleaned.substring(0, 3);
    
    // 定义有效号段
    const validPrefixes = [
        // 移动
        '134', '135', '136', '137', '138', '139',
        '150', '151', '152', '157', '158', '159',
        '178', '182', '183', '184', '187', '188', '198',
        // 联通
        '130', '131', '132', '155', '156', '166',
        '175', '176', '185', '186',
        // 电信
        '133', '153', '173', '177', '180', '181', '189', '199',
        // 虚拟运营商
        '170', '171'
    ];
    
    // 检查号段是否有效
    if (!validPrefixes.includes(prefix)) {
        return {
            cleaned: cleaned,
            valid: false,
            reason: '号段无效: 不属于已知运营商'
        };
    }
    
    // 检查号码是否过于规则（可能是不存在的号码）
    // 例如：12345678901, 11111111111等
    const allSame = /^(\d)\1{10}$/.test(cleaned);
    const sequential = /^(01234567890|12345678901|23456789012|34567890123|45678901234|56789012345|67890123456|78901234567|89012345678|90123456789)$/.test(cleaned);
    
    if (allSame) {
        return {
            cleaned: cleaned,
            valid: false,
            reason: '可疑号码: 所有数字相同',
            warning: true
        };
    }
    
    if (sequential) {
        return {
            cleaned: cleaned,
            valid: false,
            reason: '可疑号码: 连续数字',
            warning: true
        };
    }
    
    // 检查是否为测试号码模式（如13800138000等）
    const testPatterns = [
        /^13800\d{5}$/,  // 13800开头
        /^13900\d{5}$/,  // 13900开头
        /^1\d{2}000\d{4}$/  // 中间三个0
    ];
    
    for (const pattern of testPatterns) {
        if (pattern.test(cleaned)) {
            return {
                cleaned: cleaned,
                valid: false,
                reason: '可疑号码: 测试号段模式',
                warning: true
            };
        }
    }
    
    return {
        cleaned: cleaned,
        valid: true,
        reason: '格式和号段有效',
        carrier: getCarrier(prefix)
    };
}

/**
 * 获取运营商信息
 */
function getCarrier(prefix) {
    const mobilePrefixes = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '157', '158', '159', '178', '182', '183', '184', '187', '188', '198'];
    const unicomPrefixes = ['130', '131', '132', '155', '156', '166', '175', '176', '185', '186'];
    const telecomPrefixes = ['133', '153', '173', '177', '180', '181', '189', '199'];
    const virtualPrefixes = ['170', '171'];
    
    if (mobilePrefixes.includes(prefix)) return '中国移动';
    if (unicomPrefixes.includes(prefix)) return '中国联通';
    if (telecomPrefixes.includes(prefix)) return '中国电信';
    if (virtualPrefixes.includes(prefix)) return '虚拟运营商';
    return '未知';
}

/**
 * 增强版地址验证
 */
function validateAddressEnhanced(address, province, city) {
    const result = {
        valid: true,
        reason: '',
        warnings: []
    };
    
    // 检查省份是否为湖南
    if (!province || !province.includes('湖南')) {
        result.valid = false;
        result.reason = '省份不是湖南';
        return result;
    }
    
    // 检查是否有详细地址
    if (!address || address.trim().length < 4) {
        result.warnings.push('地址信息过短或缺失');
    }
    
    // 检查地址是否包含城市信息
    if (city && address && !address.includes(city)) {
        result.warnings.push('地址中可能不包含所在城市');
    }
    
    // 检查是否为明显无效地址
    const invalidPatterns = [
        '无', '不详', '未知', '不清楚', '没填', '空',
        'test', '测试', 'demo', '示例'
    ];
    
    if (address) {
        const lowerAddr = address.toLowerCase();
        for (const pattern of invalidPatterns) {
            if (lowerAddr.includes(pattern.toLowerCase())) {
                result.warnings.push(`地址可能无效: 包含"${pattern}"`);
                break;
            }
        }
    }
    
    // 检查地址格式（是否包含具体街道或门牌号）
    const hasStreet = address && (
        address.includes('路') ||
        address.includes('街') ||
        address.includes('巷') ||
        address.includes('号') ||
        address.includes('小区') ||
        address.includes('大厦')
    );
    
    if (!hasStreet) {
        result.warnings.push('地址可能不完整: 缺少街道/门牌信息');
    }
    
    if (result.warnings.length > 0) {
        result.reason = `验证通过，但有${result.warnings.length}个警告`;
    } else {
        result.reason = '地址完整有效';
    }
    
    return result;
}

/**
 * 主处理函数
 */
async function processExcelEnhanced(inputPath, outputPath) {
    console.log('开始增强版数据处理...');
    
    try {
        // 读取工作簿
        const workbook = XLSX.readFile(inputPath);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        
        // 转换为JSON数组
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        
        console.log('总数据行数:', data.length);
        
        if (data.length === 0) {
            console.log('文件为空');
            return;
        }
        
        // 定义列名
        const headers = [
            'phone', 'name', 'id_card', 'company', 'amount',
            'col5', 'col6', 'col7', 'province', 'city'
        ];
        
        const outputHeaders = [
            ...headers,
            'phone_validation', 'phone_reason', 'phone_carrier',
            'address_validation', 'address_reason', 'address_warnings',
            'status', 'notes'
        ];
        
        const outputRows = [];
        let totalRows = 0;
        let phoneValidCount = 0;
        let addressValidCount = 0;
        let fullyValidCount = 0;
        
        // 处理每一行数据
        for (let i = 0; i < data.length; i++) {
            totalRows++;
            const row = data[i];
            
            // 确保行有足够列
            if (row.length < 10) {
                console.log(`跳过第 ${i+1} 行: 列数不足`);
                continue;
            }
            
            // 验证电话号码
            const phoneResult = validatePhoneEnhanced(row[0]);
            
            // 验证地址
            const addressResult = validateAddressEnhanced(row[3], row[8], row[9]);
            
            // 判断状态
            let status = '';
            let notes = '';
            
            if (!phoneResult.valid) {
                status = '手机号无效';
                notes = phoneResult.reason;
            } else if (!addressResult.valid) {
                status = '地址无效';
                notes = addressResult.reason;
            } else {
                status = '有效';
                if (addressResult.warnings.length > 0) {
                    notes = `地址警告: ${addressResult.warnings.join('; ')}`;
                }
            }
            
            // 统计
            if (phoneResult.valid) phoneValidCount++;
            if (addressResult.valid) addressValidCount++;
            if (phoneResult.valid && addressResult.valid && addressResult.warnings.length === 0) {
                fullyValidCount++;
            }
            
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
            outputRow['phone_validation'] = phoneResult.valid ? '有效' : '无效';
            outputRow['phone_reason'] = phoneResult.reason;
            outputRow['phone_carrier'] = phoneResult.carrier || '';
            
            outputRow['address_validation'] = addressResult.valid ? '有效' : '无效';
            outputRow['address_reason'] = addressResult.reason;
            outputRow['address_warnings'] = addressResult.warnings.join('; ');
            
            outputRow['status'] = status;
            outputRow['notes'] = notes;
            
            outputRows.push(outputRow);
            
            // 显示进度
            if (totalRows % 1000 === 0) {
                console.log(`已处理 ${totalRows} 行...`);
            }
        }
        
        console.log('\n📊 处理完成:');
        console.log(`总行数: ${totalRows}`);
        console.log(`手机号有效: ${phoneValidCount} (${(phoneValidCount/totalRows*100).toFixed(2)}%)`);
        console.log(`地址有效: ${addressValidCount} (${(addressValidCount/totalRows*100).toFixed(2)}%)`);
        console.log(`完全有效(无警告): ${fullyValidCount} (${(fullyValidCount/totalRows*100).toFixed(2)}%)`);
        
        if (outputRows.length === 0) {
            console.log('没有有效数据');
            return;
        }
        
        // 准备CSV写入器
        const csvWriter = createCsvWriter({
            path: outputPath,
            header: outputHeaders.map(col => ({ id: col, title: col }))
        });
        
        // 写入数据
        await csvWriter.writeRecords(outputRows);
        console.log(`\n✅ 增强版数据已保存到: ${outputPath}`);
        
        // 生成统计报告
        generateReport(outputRows, outputPath.replace('.csv', '_report.txt'));
        
    } catch (error) {
        console.error('处理过程中出错:', error.message);
        throw error;
    }
}

/**
 * 生成统计报告
 */
function generateReport(data, reportPath) {
    let report = '='.repeat(50) + '\n';
    report += '数据验证统计报告\n';
    report += '='.repeat(50) + '\n\n';
    
    const total = data.length;
    
    // 手机号统计
    const phoneValid = data.filter(row => row.phone_validation === '有效').length;
    const phoneInvalid = total - phoneValid;
    
    // 运营商分布
    const carrierCount = {};
    data.forEach(row => {
        const carrier = row.phone_carrier || '未知';
        carrierCount[carrier] = (carrierCount[carrier] || 0) + 1;
    });
    
    // 地址统计
    const addressValid = data.filter(row => row.address_validation === '有效').length;
    const addressInvalid = total - addressValid;
    
    // 状态分布
    const statusCount = {};
    data.forEach(row => {
        const status = row.status || '未知';
        statusCount[status] = (statusCount[status] || 0) + 1;
    });
    
    // 警告统计
    const warningCount = data.filter(row => row.address_warnings && row.address_warnings.trim() !== '').length;
    
    report += `📈 总体统计:\n`;
    report += `   总记录数: ${total}\n`;
    report += `   完全有效记录: ${data.filter(row => row.status === '有效' && !row.address_warnings).length}\n`;
    report += `   有警告记录: ${warningCount}\n`;
    report += `   无效记录: ${data.filter(row => row.status !== '有效').length}\n\n`;
    
    report += `📱 手机号验证:\n`;
    report += `   有效: ${phoneValid} (${(phoneValid/total*100).toFixed(1)}%)\n`;
    report += `   无效: ${phoneInvalid} (${(phoneInvalid/total*100).toFixed(1)}%)\n\n`;
    
    report += `🏢 地址验证:\n`;
    report += `   有效: ${addressValid} (${(addressValid/total*100).toFixed(1)}%)\n`;
    report += `   无效: ${addressInvalid} (${(addressInvalid/total*100).toFixed(1)}%)\n\n`;
    
    report += `📊 状态分布:\n`;
    Object.entries(statusCount).forEach(([status, count]) => {
        report += `   ${status}: ${count} (${(count/total*100).toFixed(1)}%)\n`;
    });
    
    report += `\n📞 运营商分布:\n`;
    Object.entries(carrierCount)
        .sort((a, b) => b[1] - a[1])
        .forEach(([carrier, count]) => {
            report += `   ${carrier}: ${count} (${(count/total*100).toFixed(1)}%)\n`;
        });
    
    // 最常见的无效原因
    const invalidReasons = {};
    data.forEach(row => {
        if (row.status !== '有效') {
            const reason = row.notes || row.phone_reason || row.address_reason || '未知原因';
            invalidReasons[reason] = (invalidReasons[reason] || 0) + 1;
        }
    });
    
    if (Object.keys(invalidReasons).length > 0) {
        report += `\n⚠️ 最常见的无效原因:\n`;
        Object.entries(invalidReasons)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .forEach(([reason, count]) => {
                report += `   ${reason}: ${count} 次\n`;
            });
    }
    
    // 最常见的地址警告
    const allWarnings = [];
    data.forEach(row => {
        if (row.address_warnings) {
            const warnings = row.address_warnings.split(';').filter(w => w.trim() !== '');
            allWarnings.push(...warnings);
        }
    });
    
    const warningStats = {};
    allWarnings.forEach(warning => {
        warningStats[warning] = (warningStats[warning] || 0) + 1;
    });
    
    if (Object.keys(warningStats).length > 0) {
        report += `\n🔍 最常见的地址警告:\n`;
        Object.entries(warningStats)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .forEach(([warning, count]) => {
                report += `   ${warning}: ${count} 次\n`;
            });
    }
    
    report += `\n⏰ 报告生成时间: ${new Date().toLocaleString()}\n`;
    report += '='.repeat(50);
    
    // 写入报告文件
    fs.writeFileSync(reportPath, report, 'utf8');
    console.log(`📋 详细统计报告已生成: ${reportPath}`);
}

/**
 * 主函数
 */
async function main() {
    const inputFile = '/Users/dadaguaijiangjun/Desktop/5000.xlsx';
    const outputDir = '/Users/dadaguaijiangjun/Desktop';
    const outputFile = path.join(outputDir, '5000_enhanced_cleaned.csv');
    
    console.log('='.repeat(50));
    console.log('🔍 增强版数据清洗工具');
    console.log('='.repeat(50));
    console.log(`输入文件: ${inputFile}`);
    console.log(`输出文件: ${outputFile}`);
    console.log('处理功能:');
    console.log('  1. 手机号格式验证 (11位, 1开头)');
    console.log('  2. 手机号号段验证 (中国运营商)');
    console.log('  3. 地址省份验证 (湖南)');
    console.log('  4. 地址完整性验证');
    console.log('  5. 生成详细验证报告');
    console.log('注意: 这只是格式验证，真实的空号检测需要API服务');
    console.log('='.repeat(50));
    
    // 检查输入文件是否存在
    if (!fs.existsSync(inputFile)) {
        console.error(`❌ 输入文件不存在: ${inputFile}`);
        process.exit(1);
    }
    
    try {
        await processExcelEnhanced(inputFile, outputFile);
        console.log('\n✅ 增强版处理完成！');
        console.log(`📁 结果文件: ${outputFile}`);
        console.log(`📋 统计报告: ${outputFile.replace('.csv', '_report.txt')}`);
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

module.exports = { processExcelEnhanced };