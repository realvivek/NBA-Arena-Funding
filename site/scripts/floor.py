# The page's background: a tile of maple court flooring that repeats seamlessly, as an SVG, for light mode and a
# dark stained one for dark mode. Strips of hardwood run down the page, each made of boards of slightly different
# tones with staggered end joints, faint seams and a little grain. Writes src/assets/floor-light.svg and
# floor-dark.svg; the output is the same on every run (fixed seed).
#   python site/scripts/floor.py
import os
import random

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'assets')


def tile(palette, seam, grain, seed=7, W=336, H=672, strip=56):
    rnd = random.Random(seed)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    for i in range(W // strip):
        x = i * strip
        # board joints: two or three per strip, staggered; the strip wraps from the bottom edge to the top
        joints = sorted(rnd.sample(range(60, H - 60, 12), rnd.choice([2, 3])))
        cuts = [0] + joints + [H]
        colors = [rnd.choice(palette) for _ in range(len(cuts) - 1)]
        colors[-1] = colors[0]  # the board that crosses the tile edge has one color
        for (a, b), c in zip(zip(cuts, cuts[1:]), colors):
            out.append(f'<rect x="{x}" y="{a}" width="{strip}" height="{b - a}" fill="{c}"/>')
            for _ in range(2):  # grain: a long, gently waving line along the board
                gx = x + rnd.uniform(8, strip - 8)
                amp = rnd.uniform(1.5, 3.5)
                d = f'M{gx:.1f} {a + 2}'
                y = a + 2
                while y < b - 2:
                    y2 = min(b - 2, y + rnd.uniform(60, 120))
                    d += f' Q{gx + rnd.choice([-1, 1]) * amp:.1f} {(y + y2) / 2:.1f} {gx:.1f} {y2:.1f}'
                    y = y2
                out.append(f'<path d="{d}" fill="none" stroke="{grain}" stroke-width="1"/>')
        for j in joints:
            out.append(f'<rect x="{x}" y="{j}" width="{strip}" height="1" fill="{seam}"/>')
        out.append(f'<rect x="{x}" y="0" width="1" height="{H}" fill="{seam}"/>')
    out.append('</svg>')
    return ''.join(out)


FLOORS = {
    'light': tile(['#f6ead5', '#f3e5cc', '#f8eedd', '#f4e7d0', '#f7ebd6'], 'rgba(130,88,40,0.11)', 'rgba(130,88,40,0.05)'),
    'dark': tile(['#1c1814', '#1f1a15', '#1a1612', '#1e1915', '#1b1713'], 'rgba(255,225,180,0.06)', 'rgba(255,225,180,0.03)'),
}

if __name__ == '__main__':
    for name, svg in FLOORS.items():
        path = os.path.join(ASSETS, f'floor-{name}.svg')
        with open(path, 'w') as f:
            f.write(svg)
        print(os.path.relpath(path), len(svg), 'bytes')
