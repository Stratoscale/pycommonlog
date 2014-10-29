function pngFile( fileName )
{
    return stringEndsWith( fileName, ".png" );
}

function txtFile( fileName )
{
    return stringEndsWith( fileName, ".txt" );
}

function logFile( fileName )
{
    return stringEndsWith( fileName, ".log" ) || stringEndsWith( fileName, ".stratolog" );
}

function File( basename, rootDir )
{
    var self = this;
    self.basename = basename;
    self.rootDir = rootDir;

    self.checked = ko.observable( false );
    self.loaded = false;
    self.fileType = ko.observable("");

    self.checked.subscribe( function() {
        self.load();
    });

    self.load = function() {
        if ( self.loaded )
            return;
        self.loaded = true;
        MultiFormatLog.downloadAndParse( self.rootDir + self.basename, function( fileType, entries ) {
            self.fileType( fileType );
            for ( var i in entries ) {
                var entry = entries[ i ];
                model.logCombination.addEntry( entry );
                if (entry.level == "SUCCESS")
                    model.failedTest(false);
            }
            model.refresh();
        });
    }
}

function Directory( basename, rootDir )
{
    var self = this;
    self.basename = basename;
    self.rootDir = rootDir;

    self.subdirs = ko.observableArray([]);
    self.files = ko.observableArray([]);
    self.checked = ko.observable( false );
    self.loaded = false;

    self.doneLoading = function() {};

    self.checked.subscribe( function() {
        self.load();
    });

    self.load = function() {
        if ( self.loaded )
            return;
        self.loaded = true;
        var fullPath = self.rootDir + self.basename;
        getDirectoryListing({ url: fullPath,
            callbackPerDir: function( dirPath ) {
                self.subdirs.push( new Directory( dirPath, fullPath ) );
            },
            callbackPerFile: function( filePath ) {
                if ( pngFile( filePath ) )
                    return;
                self.files.push( new File( filePath, fullPath ) );
            },
            callbackDone: function() {
                self.doneLoading();
            },
        });
    }
}

function OpenTab( name, url )
{
    var self = this;
    self.name = name;
    self.url = url;

    self.openTab = function() {
        window.open( self.url );
    }
}

function LogDirModel()
{
    var self = this;
    self.showTree = ko.observable( false );
    self.logCombination = new LogCombination.Model();

    self.pngs = ko.observableArray([]);
    self.txts = ko.observableArray([]);
    self.subdirs = ko.observableArray([]);
    self.failedTest = ko.observable( true );

    self.rootDir = parseGetParametersFromURL().directory;
    self.rootDirectoryObject = new Directory( self.rootDir, "" );

    self.rootDirectoryObject.doneLoading = function() {
        for ( var i in self.rootDirectoryObject.files() ) {
            var file = self.rootDirectoryObject.files()[ i ];
            if ( logFile( file.basename ) )
                file.checked( true );
        }
    }

    self.load = function() {
        self.rootDirectoryObject.load();
        
        getDirectoryListing({ url: self.rootDir,
            callbackPerFile: function( filePath ) {
                if ( pngFile( filePath ) )
                    self.pngs.push( new OpenTab( filePath, self.rootDir + filePath ) );
                if ( txtFile( filePath ) )
                    self.txts.push( new OpenTab( filePath, self.rootDir + filePath ) );
            },
            callbackPerDir: function( dirPath ) {
                self.subdirs.push( new OpenTab( dirPath, self.rootDir + dirPath ) );
            },
        });
    }

    self.refresh = function() {
        self.logCombination.sort();
        self.logCombination.render();
    }

    self.showError = function() {
    }
}
