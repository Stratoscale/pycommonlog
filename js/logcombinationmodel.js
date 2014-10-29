var LogCombination = new Object();

LogCombination.Toggable = function( model, name )
{
    var self = this;
    self.model = model;
    self.name = name;
    self.enabled = ko.observable( ! LogCombination.disabled_by_default[ name ] );

    self.toggle = function() {
        self.enabled( ! self.enabled() );
        self.model.render();
    }
}

LogCombination.Column = LogCombination.Toggable;
LogCombination.Level = LogCombination.Toggable;
LogCombination.FileName = LogCombination.Toggable;

LogCombination.disabled_by_default = {
    klass: true,
    fileName: true,
    DEBUG: true,
    secondaryOrder: true,
    exception: true,
    rawMessage: true,
    imesx_trivia: true
};

LogCombination.default_order = {
    when: 1,
    level: 2,
    message: 3,
    source: 4,

    CRITICAL: 1,
    ERROR: 2,
    WARNING: 3,
    SUCCESS: 4,
    PROGRESS: 5,
    INFO: 6,
    DEBUG: 7,
};

LogCombination.Model = function()
{
    var self = this;
    self.entries = [];

    self.levels = ko.observableArray([]);
    self.columns = ko.observableArray([]);
    self.fileNames = ko.observableArray([]);

    self.columnsMap = new Object();
    self.levelsMap = new Object();
    self.fileNamesMap = new Object();

    self.addEntry = function( data ) {
        if ( ! data.level )
            data.level = "INFO"
        if ( ! data.when )
            data.when = 0;
        data.secondaryOrder = self.entries.length;
        for ( var column in data )
            if ( ! self.columnsMap[ column ] ) {
                var columnObject = new LogCombination.Column( self, column );
                self.columns.push( columnObject );
                self.columnsMap[ column ] = columnObject;
            }
        if ( ! self.fileNamesMap[ data.fileName ] ) {
            var fileName = new LogCombination.FileName( self, data.fileName );
            self.fileNames.push( fileName );
            self.fileNamesMap[ data.fileName ] = fileName;
        }
        if ( ! self.levelsMap[ data.level ] ) {
            var level = new LogCombination.Level( self, data.level );
            self.levels.push( level );
            self.levelsMap[ data.level ] = level;
        }
        self.entries.push(data);
    }
    
    self.sort = function() {
        var compare = function( a, b )
        {
            if ( a.when < b.when )
                return -1;
            if ( a.when > b.when )
                return 1;
            if ( a.secondaryOrder < b.secondaryOrder )
                return -1;
            if ( a.secondaryOrder > b.secondaryOrder )
                return 1;
            return 0;
        }
        self.entries.sort( compare );

        var reorder = function( a, b )
        {
            var aVal = LogCombination.default_order[ a.name ];
            var bVal = LogCombination.default_order[ b.name ];
            if ( ! aVal && ! bVal )
                return 0;
            if ( aVal && ! bVal )
                return -1;
            if ( ! aVal && bVal )
                return 1;
            if ( aVal < bVal )
                return -1;
            if ( aVal > bVal )
                return 1;
            return 0;
        }
        self.columns.sort( reorder );
        self.levels.sort( reorder );
    }

    self.render = function() {
        $("#logLines").html( self._html() );
    }

    self._html = function() {
        var levels = new Object();
        for ( var i in self.levels() ) {
            var level = self.levels()[ i ];
            levels[ level.name ] = level.enabled();
        }
        var renderEntryLines = [
            'var renderEntry = function( entry ) {',
            'if ( ! levels[ entry.level ] ) return "";',
            'return "<tr class=\\"" + entry.klass + "\\">" +',
        ];
        for ( var i in self.columns() ) {
            var column = self.columns()[ i ];
            if ( column.enabled() )
                if ( column.name == 'message' )
                    renderEntryLines.push( '"<td>" + entry.' + column.name + ' + rawMessage( entry ) + "</td>" +' );
                else
                    renderEntryLines.push( '"<td>" + entry.' + column.name + ' + "</td>" +' );
        }
        renderEntryLines.push( '"</tr>";}' );
        function rawMessage( entry ) {
            if ( entry.rawMessage )
                return "<pre>" + entry.rawMessage + "</pre>";
            else
                return "";
        }
        eval( renderEntryLines.join( '\n' ) );
        var renderedEntries = [];
        for ( var i in self.entries ) {
            renderedEntries.push( renderEntry( self.entries[ i ] ) );
        }
        return renderedEntries.join( '\n' );
    }
}
