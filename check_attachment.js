const XLSX = require('xlsx');
const path = require('path');

const attachmentPath = '/Users/dadaguaijiangjun/.openclaw/media/inbound/5000---010fa662-cf2c-402b-a5a9-c8aa3cabc49e.xlsx';
const desktopPath = '/Users/dadaguaijiangjun/Desktop/5000.xlsx';

console.log('检查附件文件与桌面文件是否相同...\n');

function readFileInfo(filePath) {
    try {
        const workbook = XLSX.readFile(filePath);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        
        const fs = require('fs');
        const stats = fs.statSync(filePath);
        
        return {
            size: stats.size,
            rowCount: data.length,
            colCount: data.length > 0 ? data[0].length : 0,
            sample: data.length > 0 ? data[0] : []
        };
    } catch (error) {
        return { error: error.message };
    }
}

console.log('1. 附件文件信息:');
const attachmentInfo = readFileInfo(attachmentPath);
if (attachmentInfo.error) {
    console.log(`   ❌ 错误: ${attachmentInfo.error}`);
} else {
    console.log(`   📊 文件大小: ${attachmentInfo.size} 字节`);
    console.log(`   📈 数据行数: ${attachmentInfo.rowCount}`);
    console.log(`   📉 列数: ${attachmentInfo.colCount}`);
    console.log(`   📋 第一行示例:`, attachmentInfo.sample);
}

console.log('\n2. 桌面文件信息:');
const desktopInfo = readFileInfo(desktopPath);
if (desktopInfo.error) {
    console.log(`   ❌ 错误: ${desktopInfo.error}`);
} else {
    console.log(`   📊 文件大小: ${desktopInfo.size} 字节`);
    console.log(`   📈 数据行数: ${desktopInfo.rowCount}`);
    console.log(`   📉 列数: ${desktopInfo.colCount}`);
    console.log(`   📋 第一行示例:`, desktopInfo.sample);
}

console.log('\n3. 对比结果:');
if (!attachmentInfo.error && !desktopInfo.error) {
    const sameSize = attachmentInfo.size === desktopInfo.size;
    const sameRows = attachmentInfo.rowCount === desktopInfo.rowCount;
    const sameCols = attachmentInfo.colCount === desktopInfo.colCount;
    
    console.log(`   ${sameSize ? '✅' : '❌'} 文件大小相同: ${sameSize}`);
    console.log(`   ${sameRows ? '✅' : '❌'} 行数相同: ${sameRows}`);
    console.log(`   ${sameCols ? '✅' : '❌'} 列数相同: ${sameCols}`);
    
    // 检查第一行数据是否相同
    let sameSample = true;
    if (attachmentInfo.sample.length === desktopInfo.sample.length) {
        for (let i = 0; i < attachmentInfo.sample.length; i++) {
            if (attachmentInfo.sample[i] !== desktopInfo.sample[i]) {
                sameSample = false;
                break;
            }
        }
    } else {
        sameSample = false;
    }
    console.log(`   ${sameSample ? '✅' : '❌'} 数据样本相同: ${sameSample}`);
    
    if (sameSize && sameRows && sameCols && sameSample) {
        console.log('\n🎉 结论: 两个文件完全相同！');
    } else {
        console.log('\n⚠️ 结论: 文件不完全相同，可能存在差异。');
    }
} else {
    console.log('   无法完成对比，至少一个文件读取失败。');
}

console.log('\n4. 处理结果验证:');
const outputPath = '/Users/dadaguaijiangjun/Desktop/5000_cleaned.csv';
const fs = require('fs');
if (fs.existsSync(outputPath)) {
    const outputStats = fs.statSync(outputPath);
    console.log(`   ✅ 清洗后的文件存在: ${outputPath}`);
    console.log(`   📊 文件大小: ${outputStats.size} 字节`);
    
    // 读取CSV行数
    const csvContent = fs.readFileSync(outputPath, 'utf8');
    const lines = csvContent.split('\n').filter(line => line.trim() !== '');
    console.log(`   📈 输出行数: ${lines.length} (包含表头)`);
    
    if (lines.length > 1) {
        console.log(`   📋 有效数据行数: ${lines.length - 1}`);
    }
} else {
    console.log(`   ❌ 清洗后的文件不存在: ${outputPath}`);
}