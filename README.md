# ![](hfflogo.png) HFF-Survey - QGIS plugin


##Installing from zip

### Linux/Windows/MacOS
1. Download the zip archive from github
2. Install the python packages requirements (see [Dependencies](#dependencies) paragraph)
3. Open QGIS and then from Plugin manager use Install from ZIP to install the plugin

**Note:** _While installing a message box could be prompted to warn you about missing python packages required from the plugin._

**Note2:** _Under Windows is necessary to start QGIS as Administrator when you install the plugin for the first time in order to install all the dependencies properly._

**Note3:** _If you use PostgreSQL, we raccomend to install PostgreSQL >=9.6_

**Note4:** _If you have already an hff db, use "update posgres" or "update sqlite" tool in hff configuration  form to update  your db to the new release._



#### Dependencies
* SQLAlchemy
* reportlab
* matplotlib
* networkx
* pscopgy2
* elastichserach
* pandas
* xlxswriter

The dependencies can be installed using the [modules_installer.py](/scripts/modules_installer.py) by running it from within a python shell:

```python modules_installer.py```

### Contribute
1. Fork ad clone the repository: ```git clone https://github.com/<user>/HFF.git```
2. Make your changes
3. Commit to your repository: ```git commit -am 'your_message'```
4. Create a pull request: ```git push -u origin <your_branch>```

![PR](https://services.github.com/on-demand/images/gifs/github-cli/push-and-pull.gif)
