function stringStartsWith( str, prefix )
{
    return str.indexOf( prefix ) == 0;
}

function stringEndsWith( str, suffix )
{
    return str.indexOf( suffix, str.length - suffix.length ) != -1;
}

function currentURLDirname()
{
    var href = location.href;
    if ( href.lastIndexOf( "?" ) != -1 )
        href = href.substring( 0, href.lastIndexOf( "?" ) );
    return href.substring( 0, href.lastIndexOf( "/" ) + 1 ); 
}

function deleteTerminatingSlash( path )
{
    if ( path.indexOf( "/" ) != path.length - 1 )
        return path;
    return path.substring( 0, path.length - 1 );
}

function parseGetParametersFromURL()
{
    var query = location.search.substr(1);
    var data = query.split("&");
    var result = {};
    for(var i=0; i<data.length; i++) {
        var item = data[i].split("=");
        result[item[0]] = item[1];
    }
    return result;
}

function pythonFormatString( format, args )
{
    var LETTERS = [ 's', 'd', 'f' ];
    var message;
    if ( Array.isArray( args ) ) {
        var regex = new RegExp( "%[" + LETTERS.join( "" ) + "]" );
        var msgParts = format.split( regex );
	    var countOfSpotsToAddArgs = msgParts.length - 1; 
        for ( var partsIndex = 0; partsIndex < countOfSpotsToAddArgs; partsIndex++ )
            msgParts[ partsIndex ] +=  args[ partsIndex ];
        message = msgParts.join( '' );
	    if ( countOfSpotsToAddArgs != args.length )
		    message += "-------- Reporter Warning! count of args in log message doesnt match the count of spaces to add in the message"
    }
    else {
        message = new String( format );
        for ( var str in args ) {
            for ( var letterIndex in LETTERS ) {
                var letter = LETTERS[ letterIndex ];
                message = message.replace( "%(" + str + ")" + letter, args[ str ] );
            }
        }
    }
    return message;
}

function sanitizeStringForHTML( string )
{
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;');
}
