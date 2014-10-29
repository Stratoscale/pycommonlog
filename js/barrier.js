function Barrier( doneCallback )
{
    var self = this;
    self._doneCallback = doneCallback;
    self._left = 0;

    self.wait = function( callback )
    {
        self._left += 1;
        return function() {
            var result = callback.apply( this, arguments );
            self._left -= 1;
            if ( self._left == 0 )
                self._doneCallback();
            return result;
        }
    }
}
