var MultiFormatLog = new Object();

MultiFormatLog.downloadAndParse = function( url, callback )
{
    $.get( url, function( data ) {
        MultiFormatLog.parse( data, url, callback );
    });
}

MultiFormatLog.parse = function( content, url, callback )
{
    if ( StratoLogFile.isStratoLogFile( content ) ) {
        var entries = StratoLogFile.parse( content, url );
        callback( "StratoLog", entries );
    } else if ( OpenStackLogFile.isOpenStackLogFile( content ) ) {
        var entries = OpenStackLogFile.parse( content, url );
        callback( "OpenStackLog", entries );
    } else if ( ImesxLogFile.isImesxLogFile( content ) ) {
        var entries = ImesxLogFile.parse( content, url );
        callback( "ImesxLog", entries );
    } else
        callback( "Unknown", [] );
}
