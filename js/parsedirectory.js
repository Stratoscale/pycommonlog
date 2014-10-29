function parseDirectoryListingHTML( htmlPage )
{
    if ( htmlPage.indexOf("<title>Directory listing for ") != -1 )
        return parsePythonSimpleHTTPServerDirectoryListingHTML( htmlPage );
    else
        return parseNginxDirectoryListingHTML( htmlPage );
}

function parsePythonSimpleHTTPServerDirectoryListingHTML( htmlPage )
{
    var directoryListing = { directories: [], files: [] };
    $.each( $.parseHTML( htmlPage ), function( ignoredIndex, element ) {
        if ( element.nodeName != "UL" )
            return;
        $.each( $.parseHTML( element.innerHTML ), function( ignoredIndex, element ) {
            if ( element.nodeName != "LI" )
                return;
            var path = getPathFromDirectoryListingLine( element.innerHTML );
            if ( path == "" || path == ".." || path == "../" )
                return;
            if ( stringEndsWith( path, "/" ) )
                directoryListing.directories.push( path );
            else
                directoryListing.files.push( path );
        });
    });
    return directoryListing;
}

function parseNginxDirectoryListingHTML( htmlPage )
{
    var directoryListing = { directories: [], files: [] };
    $.each( $.parseHTML( htmlPage ), function( ignoredIndex, element ) {
        if ( element.nodeName != "PRE" && element.nodeName != "TABLE" )
            return;
        var preElement = element.innerHTML;
        $.each( preElement.split( "\n" ), function( ignoredIndex, line ) {
            var path = getPathFromDirectoryListingLine( line );
            if ( path == "" || path == ".." || path == "../" )
                return;
            if ( stringEndsWith( path, "/" ) )
                directoryListing.directories.push( path );
            else
                directoryListing.files.push( path );
        });
    });
    return directoryListing;
}

function getPathFromDirectoryListingLine( line )
{
    var HREF_PREFIX = String( ' href="' );
    var hrefBeginIndex = line.indexOf( HREF_PREFIX ) + HREF_PREFIX.length;
    var hrefEndIndex = line.indexOf( '"', hrefBeginIndex );

    var linkFullPath = line.substring( hrefBeginIndex, hrefEndIndex );

    return linkFullPath;
}

function fullPathToBaseNameForDirectoryListing( path )
{
    return path.substring( path.lastIndexOf( "/", path.length - 1 ) + 1 );
}

function getDirectoryListing( options )
{
    var defaults = { url: null, callbackPerFile: function(){}, callbackPerDir: function(){}, callbackDone: function(){} };
    var settings = $.extend({}, defaults, options);
    $.get( settings.url, function( html ) {
        var directoryListing = parseDirectoryListingHTML( html );
        for ( var index in directoryListing.files ) {
            settings.callbackPerFile( directoryListing.files[ index ] );
        }
        for ( var index in directoryListing.directories ) {
            settings.callbackPerDir( directoryListing.directories[ index ] );
        }
        settings.callbackDone( directoryListing );
    });
}
