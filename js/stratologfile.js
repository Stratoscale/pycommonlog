var StratoLogFile = new Object();

StratoLogFile.isStratoLogFile = function( content )
{
    var line = content.split( "\n" )[ 0 ];
    try {
        JSON.parse( line );
        return true;
    } catch( err ) {
        return false;
    }
}

StratoLogFile.isTestFailureMessage = function( message )
{
    return stringStartsWith( message, "Test failed" ) || stringStartsWith( message, "Failed setting up" );
}

StratoLogFile.parse = function( content, fileName )
{
    var entries = [];
    lines = content.split( "\n" );
    for ( index in lines ) {
        var line = lines[ index ];
        if ( line == "" )
            continue;
        var parsed;
        try {
            parsed = JSON.parse( line );
        } catch( err ) {
            console.log( line );
            console.log( err );
        }

        var message = pythonFormatString( parsed.msg, parsed.args );
        var klass = 'message_' + parsed.levelname;
        if ( StratoLogFile.isTestFailureMessage( message ) )
            klass += " testFailureMessage";
        entries.push( { when: parsed.created,
                          message: message,
                          rawMessage: parsed.exc_text,
                          level: parsed.levelname,
                          exception: parsed.exc_text,
                          klass: klass,
                          fileName: fileName,
                          source: parsed.pathname + ":" + parsed.lineno } );
    }
    return entries;
}
