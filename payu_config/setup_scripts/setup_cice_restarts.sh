#!/bin/bash
# patch for https://github.com/open-mpi/ompi/issues/12141
if [ -f work/access-om3.cice.r.* ] ; then
    # change restart symlink to hardlink
    RESTART=$(echo work/access-om3.cice.r.*)
    ln -f $(readlink $RESTART) $RESTART
elif [ -f work/INPUT/iced.1900-01-01-10800.nc ]; then
    # no restart files yet, use initial conditions
    IC=$(readlink work/INPUT/iced.1900-01-01-10800.nc)
    rm work/INPUT/iced.1900-01-01-10800.nc
    cp $IC work/INPUT/iced.1900-01-01-10800.nc
fi
