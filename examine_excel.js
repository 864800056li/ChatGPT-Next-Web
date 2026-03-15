const XLSX = require('xlsx');
const path = require('path');

const filePath = '/Users/dadaguaijiangjun/Desktop/5000.xlsx';

console.log('检查Excel文件:', filePath);

try {
    // 读取工作簿
    const workbook = XLSX.readFile(filePath);
    
    console.log('工作表名称:', workbook.SheetNames);
    
    // 读取第一个工作表
    const sheetName = workbook.SheetNames[0];
    console.log('使用工作表:', sheetName);
    
    // 将工作表转换为JSON
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    console.log('数据行数:', data.length);
    
    // 显示前几行
    console.log('\n前5行数据:');
    for (let i = 0; i < Math.min(5, data.length); i++) {
        console.log(`行 ${i}:`, data[i]);
    }
    
    // 如果有表头，显示列名
    if (data.length > 0) {
        console.log('\n第一行（可能是表头）:', data[0]);
        console.log('列数:', data[0].length);
    }
    
    // 文件大小
    const fs = require('fs');
    const stats = fs.statSync(filePath);
    console.log('\n文件大小:', stats.size, '字节');
    
} catch (error) {
    console.error('读取文件出错:', error.message);
}