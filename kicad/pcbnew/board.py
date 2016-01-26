#  Copyright 2014 Piers Titus van der Torren <pierstitus@gmail.com>
#  Copyright 2015 Miguel Angel Ajo <miguelangel@ajo.es>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
pcbnew = __import__('pcbnew')


import kicad
from kicad.pcbnew import drawing
from kicad.pcbnew import module
from kicad.pcbnew import via
from kicad.pcbnew.track import Track
from kicad.pcbnew.via import Via
from kicad import units

class Board(object):
    def __init__(self):
        """Board object"""
        board = pcbnew.BOARD()
        self._obj = board

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        """Wraps a C++/old api BOARD object, and returns a Board."""
        return kicad.new(Board, instance)

    def add(self, obj):
        """Adds an object to the Board.

        Tracks, Drawings, Modules, etc...
        """
        self._obj.Add(obj.native_obj)
        return obj

    @property
    def modules(self):
        """Provides an iterator over the board Module objects."""
        for m in self._obj.GetModules():
            yield module.Module.wrap(m)

    @staticmethod
    def from_editor(self):
        """Provides the board object from the editor."""
        return Board.wrap(pcbnew.GetCurrentBoard())

    @staticmethod
    def load(self, filename):
        """Loads a board file."""
        return Board.wrap(pcbnew.LoadBoard(filename))

    def save(self, filename=None):
        """Save the board to a file.

        filename should have .kicad_pcb extention.
        """
        if filename is None:
            filename = self._obj.GetFileName()
        self._obj.Save(filename)

    def add_module(self, ref, pos=(0, 0)):
        """Create new module on the board"""
        return module.Module(ref, pos, board=self)

    @property
    def default_width(self, width=None):
        b = self._obj
        return (
            float(b.GetDesignSettings().GetCurrentTrackWidth()) /
            units.DEFAULT_UNIT_IUS)

    def add_track_segment(self, start, end, layer='F.Cu', width=None):
        """Create a track segment."""

        track = Track(width or self.default_width,
                      start, end, layer, board=self)
        self._obj.Add(track.native_obj)
        return track

    def get_layer(self, name):
        return self._obj.GetLayerID(name)

    def add_track(self, coords, layer='F.Cu', width=None):
        """Create a track polyline.

        Create track segments from each coordinate to the next.
        """
        for n in range(len(coords) - 1):
            self.add_track_segment(coords[n], coords[n + 1],
                                   layer=layer, width=width)

    @property
    def default_via_size(self):
        return (float(self._obj.GetDesignSettings().GetCurrentViaSize()) /
                units.DEFAULT_UNIT_IUS)

    @property
    def default_via_drill(self):
        via_drill = self._obj.GetDesignSettings().GetCurrentViaDrill()
        if via_drill > 0:
            return (float(via_drill) / units.DEFAULT_UNIT_IUS)
        else:
            return 0.2

    def add_via(self, coord, via_type=via.THROUGH, layer_pair=('B.Cu', 'F.Cu'), size=None,
                drill=None):
        """Create a via on the board.

        :param via_type: type of the via (default:via.THROUGH, via.BURIED, via.MICRO).
        :param coord: Position of the via.
        :param layer_pair: Tuple of the connected layers (for example
                           ('B.Cu', 'F.Cu')).
        :param size: size of via in mm, or None for current selection.
        :param drill: size of drill in mm, or None for current selection.
        :returns: the created Via
        """
        return self.add(
            Via(coord, via_type, layer_pair, size or self.default_via_size,
                drill or self.default_via_drill, board=self))


    def add_line(self, start, end, layer='F.SilkS', width=0.15):
        """Create a graphic line on the board"""
        return self.add(
            drawing.Segment(start, end, layer, width, board=self))

    def add_polyline(self, coords, layer='F.SilkS', width=0.15):
        """Create a graphic polyline on the board"""
        for n in range(len(coords) - 1):
            self.add_line(coords[n], coords[n + 1], layer=layer, width=width)

    def add_circle(self, center, radius, layer='F.SilkS', width=0.15):
        """Create a graphic circle on the board"""
        return self.add(
            drawing.Circle(center, radius, layer, width, board=self))

    def add_arc(self, center, radius, start_angle, stop_angle,
                layer='F.SilkS', width=0.15):
        """Create a graphic arc on the board"""
        return self.add(
            drawing.Arc(center, radius, start_angle, stop_angle,
                        layer, width, board=self))

    def SetCopperLayerCount(self, n):
        self._obj.SetCopperLayerCount(n)

    def SetBoardThickness(self, size):
        self._obj.SetBoardThickness(int(size * units.DEFAULT_UNIT_IUS))

    def SetBlindBuriedViaAllowed(self, flag=True):
        settings = self._obj.GetDesignSettings()
        settings.m_BlindBuriedViaAllowed = flag
        self._obj.SetDesignSettings(settings)

    def add_track(self, path, layer=None, width=None):
        for i in xrange(len(path)-1):
            self.add_track_segment(path[i], path[i+1], layer=layer, width=width)




