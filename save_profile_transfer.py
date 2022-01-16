import sys
import os
import time
import shutil
from pathlib import Path

if "mobase" not in sys.modules:
    import mock_mobase as mobase
from typing import List


class save_profile_transfer(mobase.IPlugin):
    __organizer: mobase.IOrganizer

    NAME = "save_profile_transfer"
    DESCRIPTION = "moves profile save to all profiles"

    def __init__(self):
        super().__init__()  # You need to call this manually.
        self.__organizer = None
        self.__parentWidget = None

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self.__organizer = organizer
        self.__organizer.onFinishedRun(lambda appName, result: self.move_save())
        return True

    def name(self) -> str:
        return self.NAME

    def author(self) -> str:
        return "JanuarySnow"

    def description(self) -> str:
        return self.DESCRIPTION

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)

    def isActive(self):
        return bool(self.__organizer.pluginSetting(self.NAME, "enabled"))

    def settings(self) -> List[mobase.PluginSetting]:
        return [mobase.PluginSetting("enabled", "enable this plugin", True)]

    def move_save(self) -> None:
        managedGame = self.__organizer.managedGame()
        gameSavesDirectory = managedGame.savesDirectory().absolutePath()
        if self.__organizer.profile().localSavesEnabled():
            gameSavesDirectory = os.path.join(
                self.__organizer.profile().absolutePath(), "saves"
            )
        if not os.path.exists(gameSavesDirectory):
            return
        save_list = [
            os.path.join(gameSavesDirectory, f)
            for f in os.listdir(gameSavesDirectory)
            if os.path.isfile(os.path.join(gameSavesDirectory, f))
        ]
        profiles_path = self.__organizer.profilePath()  # mo2/profiles/default
        profiles_path = Path(profiles_path).parents[0]  # mo2/profiles/
        save_list = self.filter_list(save_list)
        if not save_list:
            return
        directories = self.listdirs(profiles_path)
        for x in directories:
            savepath = os.path.join(os.path.join(profiles_path, x), "saves")
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            for y in save_list:
                head, source_file = os.path.split(y)
                dest_file = os.path.join(savepath, source_file)
                if os.path.exists(dest_file):
                    if os.path.samefile(y, dest_file):
                        continue
                    os.remove(dest_file)
                shutil.copy2(y, savepath)

    def listdirs(self, folder):
        return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

    def filter_list(self, files):
        return filter(lambda f: time.time() - os.path.getmtime(f) < 172800, files)


def createPlugin() -> mobase.IPlugin:
    return save_profile_transfer()
