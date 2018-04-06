.. DesignTeamMDO documentation file

==========================
Building the Documentation
==========================

In the directory that the 'DesignTeamMDO' folder lives, create a new folder called 'DesignTeamMDO-Docs'.::

    mkdir DesignTeamMDO-Docs

Now, in this directory, there should be two folders, one called 'DesignTeamMDO' and one called 'DesignTeamMDO-Docs'. Change to the documentation folder with::

    cd DesignTeamMDO-Docs

Within this folder, checkout the git repository and select the special GitHub Pages 'gh-pages' branch with the following commands.::

    git clone https://cessnao3@github.com/mach-m-fly/DesignTeamMDO.git html
    cd html
    git checkout gh-pages

Now, documentation folder is properly setup. We can return to the original 'DesignTeamMDO' folder for the remaining commands.

In order to build the documentation, first run the 'sphinx-apidoc-get.sh' file in the root project directory.::

    bash sphinx-apidoc-get.sh

Then, change directories to the 'doc' folder and run the make command to generate the html files.::

    make clean
    make html

To view the newly created html files with the documentation, open the 'DesignTeamMDO-Docs/html/index.html' file in your favorite web browser.

From here, in order to get the html files updated on the GitHub Pages, simply add and push the files in the 'DesignTeamMDO-Docs/html' folder, as follows::

    git add --all
    git commit -m <ENTER A HELPFUL MESSAGE>
    git push

