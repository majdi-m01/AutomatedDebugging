from typing import Optional, List


class Train:

    def __init__(self, train_id: int):
        self.train_id = train_id


class Track:

    def repOK(self):
        # TODO: implement the function that verifies whether this track is in a valid state
        assert self.start is not self.end

    def __init__(self, start, end, train: Optional[Train] = None):
        self.start = start
        self.end = end
        self.train = train
        self.repOK()

    def set_train(self, train: Train):
        self.repOK()
        # TODO: add preconditions
        assert train is not None
        assert self.train is None
        self.train = train
        self.repOK()

    def remove_train(self):
        self.repOK()
        self.train = None
        self.repOK()


class Station:

    def repOK(self):
        # TODO: implement the function that verifies whether this station is in a valid state
        endpoint = False
        for t in self.tracks:
            if self is t.start or self is t.end:
                endpoint = True
        assert endpoint

    def __init__(self, tracks: Optional[List[Track]] = None):
        self.tracks = tracks if tracks else []
        self.repOK()

    def add_track(self, track: Track):
        self.repOK()
        self.tracks.append(track)
        self.repOK()


class TrainNetwork:

    def repOK(self):
        # TODO: implement the function that verifies whether this train network is in a valid state
        train_ids = []
        for train in self.trains:
            train_ids.append(train.train_id)
        assert len(set(train_ids)) == len(train_ids)

    def __init__(self, stations: Optional[List[Station]] = None,
                 tracks: Optional[List[Track]] = None,
                 trains: Optional[List[Train]] = None):
        self.stations = stations if stations else []
        self.tracks = tracks if tracks else []
        self.trains = trains if trains else []
        self.repOK()

    def add_station(self, station: Station):
        self.repOK()
        self.stations.append(station)
        self.repOK()

    def add_track(self, track: Track):
        self.repOK()
        self.tracks.append(track)
        self.repOK()

    def add_train(self, train: Train):
        self.repOK()
        self.trains.append(train)
        self.repOK()

    def move_train(self, train: Train, from_track: Track, to_track: Track):
        self.repOK()
        # TODO: add preconditions
        assert from_track.train is train
        assert to_track.train is None
        assert train in self.trains
        assert to_track.start is from_track.end
        from_track.remove_train()
        to_track.set_train(train)
        self.repOK()


################################ Tests ################################


from debuggingbook.ExpectError import ExpectError
import sys


def create_track(start_station: Station, end_station: Station, train: Optional[Train] = None):
    track = Track(start_station, end_station, train)
    start_station.add_track(track)
    end_station.add_track(track)
    return track


def build_network(two_trains=True):
    train_0 = Train(0)
    if two_trains:
        train_1 = Train(1)
    station_0 = Station()
    station_1 = Station()
    station_2 = Station()
    station_3 = Station()
    station_4 = Station()
    track_0 = create_track(station_0, station_1, train_0)
    track_1 = create_track(station_1, station_2)
    track_2 = create_track(station_1, station_2)
    track_3 = create_track(station_2, station_3)
    track_4 = create_track(station_3, station_4, train_1 if two_trains else None)
    track_5 = create_track(station_4, station_0)
    return TrainNetwork(
        stations=[station_0, station_1, station_2, station_3, station_4],
        tracks=[track_0, track_1, track_2, track_3, track_4, track_5],
        trains=[train_0, train_1] if two_trains else [train_0]
    )


def test_ok():
    network = build_network()
    network.move_train(network.trains[0], network.tracks[0], network.tracks[1])
    network.move_train(network.trains[1], network.tracks[4], network.tracks[5])
    network.move_train(network.trains[0], network.tracks[1], network.tracks[2])
    network.move_train(network.trains[0], network.tracks[2], network.tracks[3])
    network.move_train(network.trains[1], network.tracks[5], network.tracks[0])


def test_illegal_move():
    network = build_network()
    try:
        network.move_train(network.trains[1], network.tracks[4], network.tracks[5])
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_illegal_move2():
    network = build_network()
    network.move_train(network.trains[0], network.tracks[0], network.tracks[1])
    try:
        network.move_train(network.trains[0], network.tracks[1], network.tracks[3])
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_illegal_move3():
    network = build_network(two_trains=False)
    try:
        network.move_train(network.trains[0], network.tracks[0], network.tracks[3])
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_illegal_move4():
    network = build_network(two_trains=False)
    try:
        network.move_train(Train(1), network.tracks[0], network.tracks[3])
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_trains_with_same_id():
    try:
        TrainNetwork(trains=[Train(0), Train(0)])
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_track_occupied():
    track = create_track(Station(), Station(), Train(0))
    try:
        track.set_train(Train(1))
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_track_has_not_station():
    station_0, station_1, station_2 = Station(), Station(), Station()
    track = Track(station_0, station_1)
    try:
        station_2.add_track(track)
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test_track_does_not_exist():
    network = build_network(two_trains=False)
    track = create_track(network.stations[0], network.stations[1])
    try:
        network.move_train(network.trains[0], network.tracks[0], track)
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{sys._getframe(0).f_code.co_name} failed')


def test():
    test_ok()
    test_illegal_move()
    test_illegal_move2()
    test_illegal_move3()
    test_illegal_move4()
    test_trains_with_same_id()
    test_track_occupied()
    test_track_has_not_station()
    test_track_does_not_exist()


if __name__ == '__main__':
    test()
