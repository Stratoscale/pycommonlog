var ImesxLogFile = new Object();

ImesxLogFile.isImesxLogFile = function( content )
{
    var line = content.split( "\n" )[ 0 ];
    return line.search( 'Section for VMware VirtualCenter' ) != -1;
}

ImesxLogFile.parse = function( content, fileName )
{
    var entries = [];
    lines = content.split( "\n" );
    var previous_entry = new Object();
    var localTimeSyncValue = 0;
    var vCenterTimeSyncValue = 0;
    for ( index in lines ) {
        var line = lines[ index ];
        var fields = line.split( " " );
        if ( line == "" || line.slice( 0, 4) == 'mem>' || fields[ 0 ] == '------' || fields[ 0 ] == 'Section' )
            continue;
        if ( line.substring( 0, 3 ) == '-->' ){
            previous_entry.message = previous_entry.message + '\n' + line.slice( 3 );
            continue;
        }
        if ( line.search( 'Sync Timestamp' ) != -1 ){
            fields = line.split( '#' );
            if ( fields.length == 3 )
                localTimeSyncValue = parseFloat( fields[ 1 ] )
                vCenterTimeSyncValue = ImesxLogFile.parseDateTime( fields[ 2 ] );
            continue;
        }

        var lineTime = ImesxLogFile.parseDateTime( fields[ 0 ] ) - vCenterTimeSyncValue + localTimeSyncValue;
        var message = fields.slice( 1 ).join( ' ' );
        var levelSource = ImesxLogFile.parseSourceAndLevel( message );
        var level = 'imesx_' + levelSource[ 0 ];
        var source = levelSource[ 1 ];
        source = source.split( "'" ).join( "" );
        message = sanitizeStringForHTML( message.slice( message.indexOf( ']' ) + 1 ) );

        var klass = 'message_IMESX';
        previous_entry = new Object( { when: lineTime,
                          message: message,
                          level: level,
                          exception: null,
                          klass: klass,
                          fileName: fileName,
                          source: source } );
        entries.push( previous_entry );
    }
    return entries;
}

ImesxLogFile.parseDateTime = function( datetimeString )
{
    datetimeString = datetimeString.slice( 0, datetimeString.indexOf( 'Z' ) );
    var datetime = datetimeString.split( 'T' );
    var date = datetime[0].split( '-' );
    var yyyy = date[0];
    var mm = date[1]-1;
    var dd = date[2];

    var time = datetime[1].split( ":" );
    var h = parseInt( time[0] ) + 2;
    if ( h >= 24 )
        h = h - 24;
    var m = time[1];
    var s = parseInt( time[2] ) + 1; //get rid of that 00.0;
    var ms = parseFloat( "0." + time[2].split( "." )[ 1 ] ) * 1000;

    return ( new Date(yyyy,mm,dd,h,m,s,ms) ).valueOf() / 1000.0;
}

ImesxLogFile.parseSourceAndLevel = function( messageString )
{
    var sourceSection = messageString.split( ']' )[0].slice( 1 ).split( ' ' );
    return sourceSection.slice( 1 );
}
