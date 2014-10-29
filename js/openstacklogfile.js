var OpenStackLogFile = new Object();

OpenStackLogFile.isOpenStackLogFile = function( content )
{
    var line = content.split( "\n" )[ 0 ];
    return line.indexOf( " [-] ", line ) != -1;
}

OpenStackLogFile.parse = function( content, fileName )
{
    var entries = [];
    lines = content.split( "\n" );
    for ( index in lines ) {
        var line = lines[ index ];
        if ( line == "" )
            continue;
        var fields = line.split( " " );
        var date = fields[ 0 ];
        var time = fields[ 1 ];
        var pid = fields[ 2 ];
        var level = fields[ 3 ];
        var source = fields[ 4 ];
        var message = sanitizeStringForHTML( fields.slice( 5 ).join( " " ) );

        var klass = 'message_' + level;
        entries.push( { when: OpenStackLogFile.parseDateTime( date, time ),
                          message: message,
                          level: level,
                          exception: null,
                          klass: klass,
                          fileName: fileName,
                          source: source } );
    }
    return entries;
}

OpenStackLogFile.parseDateTime = function( dateString, timeString )
{
    var date = dateString.split("-");
    var yyyy = date[0];
    var mm = date[1]-1;
    var dd = date[2];

    var time = timeString.split(":");
    var h = time[0];
    var m = time[1];
    var s = parseInt(time[2]); //get rid of that 00.0;
    var ms = parseFloat( "0." + time[2].split( "." )[ 1 ] ) * 1000;

    return ( new Date(yyyy,mm,dd,h,m,s,ms) ).valueOf() / 1000.0;
}
