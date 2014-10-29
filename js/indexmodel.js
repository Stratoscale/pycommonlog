function testDir( dirName )
{
    return dirName.indexOf( "test" ) != -1;
}

function hasAMessageWithSuccessLevel( entries )
{
    for ( var index in entries )
        if ( entries[ index ].level == "SUCCESS" )
            return true;
    return false;
}

function fetchTestResult( rootUrl, dirName )
{
    $.get( testLogFileName( rootUrl, dirName ), function( data ) {
        var entries = StratoLogFile.parse( data );
        var testSucceeded = hasAMessageWithSuccessLevel( entries );
        var test = new Test({ failedTest: ! testSucceeded, rootUrl: rootUrl, dirName: dirName });
        if ( testSucceeded )
            model.passedTests.push( test );
        else
            model.failedTests.push( test );
    });
}

function testLogFileName( rootUrl, dirName )
{
    return rootUrl + dirName + "/test.stratolog";
}

function getRootURL()
{
    return currentURLDirname() + "../";
}

function Test( data )
{
    var self = this;
    self.testRootDir = data.rootUrl + data.dirName;
    self.name = ko.observable( data.dirName );

    self.openTestPage = function() {
        location.href = "logdir.html?directory=" + self.testRootDir;
    }
}

function IndexModel()
{
    var self = this;
    self.failedTests = ko.observableArray([]);
    self.passedTests = ko.observableArray([]);

    self.load = function() {
        self.failedTests.removeAll();
        self.passedTests.removeAll();
        getDirectoryListing({ url: getRootURL(), callbackPerDir: function( dirPath ) {
            if ( testDir( dirPath ) )
                fetchTestResult( getRootURL(), dirPath );
        }});
    }
}
