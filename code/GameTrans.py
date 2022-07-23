
import winreg
import os
import json
import re
import copy
import shutil
from googletrans import Translator

GAME_ID = 1794680	# Vampire Survivors game id
LANG_PATH = "resources/app/.webpack/renderer/assets/lang"

SRC_LANG = "en"
# 需要翻译的语言
DST_LANG = "zh-CN"


class CRegTool(object):

	@classmethod
	def GetSteamAppInstallPath(cls, iSteamAppID):
		# 直接读注册表获取对应steamid游戏的安装位置
		sSteamAppRegPath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam App {}".format(iSteamAppID)
		hReg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sSteamAppRegPath)
		sPath, _ = winreg.QueryValueEx(hReg, "InstallLocation")
		return sPath

class CTransTool(object):

	def __init__(self):
		self.m_Translator = Translator()

	@classmethod
	def IsHasCN(cls, text):
		# 检查文本中是否有中文
		sPattern = re.compile(u'[\u4e00-\u9fa5]+')
		if sPattern.search(text):
			return True
		return False


	@classmethod
	def GetJsonData(cls, sJsonPath):
		try:
			with open(sJsonPath, "rb") as f:
				return json.loads(f.read())
		except IOError as e:
			print("加载json文件异常 :", sJsonPath, e)
		return {}

	@classmethod
	def IterDict(cls, data, dCopy):
		for k, v in data.items():
			if isinstance(v, dict):
				yield from cls.IterDict(v, dCopy[k])
			else:
				yield dCopy, k, v


	def TransFile(self, sFilePath):
		"""
			结构大概是
			{
				"zh-CN":{
					"english": "Chinese",
					"native": "简体中文",
					"api": "schinese",
					"translations":{
						"CLOVER": {
							"description": "拾取增加 10% 的幸运值",
							"name": "三叶草"
						}, "COIN": {
							"description": "Adds 1 to your gold coins total.",
							"name": "Gold Coin"
						},
					}
				}
			}
		"""

		data = self.GetJsonData(sFilePath)
		if not data or not isinstance(data, dict):
			return {}
		# 只接受dict

		dRet = copy.deepcopy(data)
		dDstLang = data.get(DST_LANG, {}).get("translations", {})

		for dOutDict, sKey, sText in self.IterDict(dDstLang, dRet.get(DST_LANG, {}).get("translations", {})):
			if self.IsHasCN(sText):
				continue

			sTrans = self.m_Translator.translate(sText, DST_LANG).text
			if not sTrans:
				continue

			dOutDict[sKey] = sTrans
			print("翻译 :[{}] -> [{}]".format(sText, sTrans))

		return dRet


def Main():
	sPath = CRegTool.GetSteamAppInstallPath(GAME_ID)
	sFullPath = os.path.join(sPath, LANG_PATH)

	if not os.path.exists(sFullPath):
		print("找不到对应游戏路径")
		return

	# copy back
	if not os.path.exists(sFullPath + "_back"):
		shutil.copytree(sFullPath, sFullPath + "_back")

	oTool = CTransTool()

	for sRoot, lDirs, lFiles in os.walk(sFullPath):
		for sFile in lFiles:
			if not sFile.endswith(".json"):
				continue
			sPath = os.path.join(sRoot, sFile).replace("\\", "/")
			print("=" * 20)
			print("开始翻译：", sPath)
			dRet = oTool.TransFile(sPath)
			if not dRet:
				print("翻译失败，跳过")
				continue
			sJson = json.dumps(dRet, sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False)
			with open(sPath, "wb") as f:
				f.write(sJson.encode(encoding='UTF-8'))
			print("翻译完成：", sPath)

if __name__ == "__main__":
	Main()
	os.system("pause")
