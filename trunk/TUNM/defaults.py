__all__ = ['initials', 'bounds', 'time']

initials = {
    "Switch": {
        "t0": 1.,
    },
    "Router": {
        "t0": 1.,
    },
    "End": {
        "t0": 1.,
    }
}

bounds = {
    "Switch": {
        "t0": {
            "left": float(0.),
            "right": float("inf")
        },
    },
    "Router": {
        "t0": {
            "left": float(0.),
            "right": float("inf")
        },
    },
    "End": {
        "t0": {
            "left": float(0.),
            "right": float("inf")
        },
    }
}

time = 5.