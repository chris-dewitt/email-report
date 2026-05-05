from vollab.surface.builder import build_surface, interpolate_vol, sample_skew_surface


def test_sample_surface_has_skew():
    strikes, expiries, vols = sample_skew_surface(100)
    atm_idx = strikes.index(100.0)
    otm_put_idx = strikes.index(80.0)
    for i in range(len(expiries)):
        assert vols[i][otm_put_idx] > vols[i][atm_idx], "OTM put vol should exceed ATM"


def test_surface_points_count():
    strikes, expiries, vols = sample_skew_surface()
    points = build_surface(strikes, expiries, vols)
    assert len(points) == len(strikes) * len(expiries)


def test_interpolation_at_grid_point():
    strikes, expiries, vols = sample_skew_surface()
    vol = interpolate_vol(strikes, expiries, vols, strikes[4], expiries[2])
    assert abs(vol - vols[2][4]) < 0.001


def test_interpolation_between_grid():
    strikes, expiries, vols = sample_skew_surface()
    vol = interpolate_vol(strikes, expiries, vols, 97.5, 0.375)
    assert 0.05 < vol < 0.50


def test_moneyness_computed():
    strikes, expiries, vols = sample_skew_surface(100)
    points = build_surface(strikes, expiries, vols, 100)
    atm_points = [p for p in points if p.strike == 100]
    assert all(p.moneyness == 1.0 for p in atm_points)
