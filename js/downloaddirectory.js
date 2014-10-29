function downloadDirectory( options )
{
    var defaults = { regex: "", downloadedCallback: function(){}, doneCallback: function(){}, json: false };
    var settings = $.extend({}, defaults, options);
    var regex = new RegExp( settings.regex );
    var barrier = new Barrier( settings.doneCallback );
    if ( settings.url[ settings.url.length - 1 ] != '/' )
        settings.url = settings.url + '/';
    getDirectoryListing( { url: settings.url, callbackPerFile: function( filename ) {
            if ( ! regex.test( filename ) )
                return;
            if ( settings.json )
                $.getJSON( settings.url + "/" + filename, barrier.wait( settings.downloadedCallback ) );
            else 
                $.get( settings.url + "/" + filename, barrier.wait( settings.downloadedCallback ) );
        },
        callbackDone: barrier.wait(function(){}) });
}
