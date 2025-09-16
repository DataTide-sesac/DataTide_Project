import PublicFunc as pf
import pandas as pd

filePath = './data/sample/부산_울산/수온'
fileName = '부산_수온_2025_02_월간보고서.pdf'
func = pf.PublicFunc()

testPDF = func.ReadPDF(filePath,fileName)

# print(testPDF.tail)
# print(testPDF.isnull().sum())

print(testPDF)

func.SaveCSV(testPDF,'testPDF1.csv')
