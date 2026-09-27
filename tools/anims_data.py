"""Hollow Oath animation set (R6 + Earth Golem rig). See animkit.py for the pose conventions:
  pitch +: limbs forward / torso & head back | yaw +: turn left | roll +: right limbs out, left limbs in, torso lean left
  'd': RootJoint (torso) offset in studs. Frames at 30 fps. Easing on a key shapes the motion ARRIVING at that key
  ('out' = fast snap that settles: used for strikes; 'in' = accelerating; 'cubic' = ease in/out; 'constant' = hold).
"""
from animkit import Anim, Rig


def P(base, **over):
    p = dict(base)
    for k, v in over.items():
        p[k] = v
    return p


def mirror(p):
    """Mirror a pose left <-> right (yaw and roll flip, rs<->ls, rh<->lh)."""
    out = {}
    swap = {'rs': 'ls', 'ls': 'rs', 'rh': 'lh', 'lh': 'rh'}
    for k, v in p.items():
        if k == 'd':
            out['d'] = (-v[0], v[1], v[2]); continue
        pitch, yaw, roll = v
        out[swap.get(k, k)] = (pitch, -yaw, -roll)
    return out


R6 = Rig(1.0, 'R6')
GOLEM = Rig(2.4, 'Golem')

# ---------------------------------------------------------------------------------------------------- base poses
N = dict(root=(0, 0, 0), neck=(0, 0, 0), rs=(0, 0, 4), ls=(0, 0, -4), rh=(0, 0, 2), lh=(0, 0, -2))
# sword stance: bladed right-foot-forward, sword held forward-up in the right hand, left hand near the hilt
S0 = dict(root=(-6, -20, 0), neck=(-2, 18, 0), rs=(42, 8, 6), ls=(40, 0, 26), rh=(12, 20, 6), lh=(-10, 20, -6), d=(0, -0.08, 0))
# fist guard
F0 = dict(root=(-8, -15, 0), neck=(-4, 14, 0), rs=(78, 0, -24), ls=(84, 0, 24), rh=(10, 15, 6), lh=(-10, 15, -6), d=(0, -0.12, 0))
AIR = dict(root=(-4, 0, 0), neck=(0, 0, 0), rs=(60, 0, 20), ls=(60, 0, -20), rh=(28, 0, 4), lh=(-8, 0, -4))
LUNGE_LEGS = dict(rh=(38, 20, 6), lh=(-34, 20, -6))


def legs_for_yaw(y, fwd=12, back=-10, spread=6):
    """Counter-rotate the legs so the feet stay facing forward while the torso twists by yaw y."""
    return dict(rh=(fwd, -y, spread), lh=(back, -y, -spread))


ANIMS = []


def add(name, keys, **kw):
    ANIMS.append(Anim('HO_Anim_' + name, keys, **kw))


# ================================================================================================= SWORD
add('Sword_Idle', [
    (0, S0, 'cubic'),
    (30, P(S0, d=(0, -0.16, 0), rs=(45, 8, 6), ls=(43, 0, 26), neck=(-4, 18, 0)), 'cubic'),
    (60, S0, 'cubic')], loop=True, priority='Idle', notes='Bladed stance, slow breathing.')

add('Sword_Combo1', [
    (0, S0, 'cubic'),
    (4, P(S0, root=(-5, -48, 0), rs=(96, 0, 72), ls=(22, 0, 8), neck=(-2, 45, 0), **legs_for_yaw(-48)), 'cubic'),
    (8, P(S0, root=(-9, 36, 0), rs=(86, 0, -56), ls=(28, 0, -12), neck=(-4, -30, 0), d=(0, -0.18, 0), **legs_for_yaw(36)), 'out'),
    (12, P(S0, root=(-7, 52, 0), rs=(70, 0, -78), ls=(20, 0, -20), neck=(-4, -42, 0), d=(0, -0.14, 0), **legs_for_yaw(52)), 'out'),
    (18, S0, 'cubic')], markers={'Hit': 8}, notes='Horizontal slash right-to-left.')

add('Sword_Combo2', [
    (0, S0, 'cubic'),
    (3, P(S0, root=(-12, 42, 0), rs=(38, 0, -72), ls=(20, 0, -10), d=(0, -0.24, 0), neck=(0, -36, 0), **legs_for_yaw(42)), 'cubic'),
    (7, P(S0, root=(-2, -42, 0), rs=(132, 0, 46), ls=(40, 0, 30), d=(0, -0.08, 0), neck=(4, 38, 0), **legs_for_yaw(-42)), 'out'),
    (11, P(S0, root=(0, -56, 0), rs=(150, 0, 60), ls=(35, 0, 36), neck=(6, 48, 0), **legs_for_yaw(-56)), 'out'),
    (18, S0, 'cubic')], markers={'Hit': 7}, notes='Rising backhand left-to-right.')

add('Sword_Combo3', [
    (0, S0, 'cubic'),
    (5, P(S0, root=(9, -10, 0), rs=(172, 0, 10), ls=(162, 0, 22), neck=(10, 10, 0), d=(0, 0.05, 0)), 'cubic'),
    (11, P(S0, root=(-30, -5, 0), rs=(52, 0, 2), ls=(46, 0, 16), neck=(-12, 5, 0), d=(0, -0.42, 0), rh=(38, 5, 6), lh=(-32, 5, -6)), 'out'),
    (15, P(S0, root=(-36, -5, 0), rs=(32, 0, 2), ls=(28, 0, 16), neck=(-14, 5, 0), d=(0, -0.46, 0), rh=(40, 5, 6), lh=(-34, 5, -6)), 'out'),
    (22, S0, 'cubic')], markers={'Hit': 11}, notes='Overhead vertical cut into a lunge.')

_coil = P(S0, root=(-15, -80, 0), rs=(90, 0, 80), ls=(60, 0, -18), neck=(0, 70, 0), d=(0, -0.5, 0), rh=(40, 80, 8), lh=(-40, 80, -8))
_fin = P(S0, root=(-26, 340, 0), rs=(100, 0, -62), ls=(18, 0, -30), neck=(-10, 20, 0), d=(0, -0.62, 0), rh=(42, 20, 8), lh=(-42, 20, -8))
add('Sword_Finisher', [
    (0, S0, 'cubic'),
    (8, _coil, 'cubic'),
    (12, P(_coil, root=(-10, 60, 0), rs=(90, 0, -10), neck=(0, -40, 0), d=(0, -0.25, 0), rh=(20, -60, 8), lh=(-20, -60, -8)), 'in'),
    (16, P(_coil, root=(-8, 180, 0), rs=(92, 0, -20), neck=(0, 0, 0), d=(0, -0.2, 0), rh=(15, 0, 8), lh=(-15, 0, -8)), 'linear'),
    (20, P(_coil, root=(-12, 290, 0), rs=(96, 0, 10), neck=(0, 30, 0), d=(0, -0.3, 0), rh=(25, 0, 8), lh=(-25, 0, -8)), 'linear'),
    (24, _fin, 'out'),
    (34, P(_fin, d=(0, -0.66, 0)), 'constant'),
    (46, P(S0, root=(-6, 340, 0)), 'cubic')],
    markers={'Hit': 16, 'Hit2': 24}, notes='Heavy 4th hit: coil, full spin cut (Hit), final heavy slash (Hit2) held for 10 frames.')

_block = P(S0, root=(-10, -10, 0), rs=(96, -10, -36), ls=(82, 0, 32), neck=(-4, 8, 0), d=(0, -0.16, 0), **legs_for_yaw(-10))
add('Sword_Block', [(0, _block, 'cubic'), (10, P(_block, d=(0, -0.2, 0)), 'cubic'), (20, _block, 'cubic')],
    loop=True, priority='Action', notes='Blade held horizontal across the body (loop while blocking).')

add('Sword_Parry', [
    (0, S0, 'cubic'),
    (3, P(S0, rs=(122, 0, -22), root=(-5, 20, 0), ls=(30, 0, 10), neck=(0, -12, 0), **legs_for_yaw(20)), 'out'),
    (7, P(S0, rs=(136, 0, -6), root=(-2, 26, 0), neck=(2, -16, 0), **legs_for_yaw(26)), 'out'),
    (14, S0, 'cubic')], markers={'Hit': 3}, notes='Snap deflect; Hit = parry window frame.')

_lock = P(S0, root=(-20, 0, 0), rs=(95, 0, -10), ls=(90, 0, 20), neck=(-12, 0, 0), d=(0, -0.3, 0), rh=(32, 0, 6), lh=(-36, 0, -6))
add('Sword_ClashLock', [
    (0, _lock, 'cubic'), (6, P(_lock, rs=(97, 2, -8), root=(-22, 2, 0)), 'linear'), (12, P(_lock, rs=(94, -2, -11), root=(-19, -1, 0)), 'linear'),
    (18, P(_lock, rs=(96, 1, -9), root=(-23, 1, 0), d=(0, -0.34, 0)), 'linear'), (24, _lock, 'linear')],
    loop=True, priority='Action2', notes='Blades locked, straining tremble (loop).')

for dname, pose in (
        ('Forward', P(S0, root=(-36, 0, 0), rs=(-42, 0, 16), ls=(-40, 0, -16), neck=(20, 0, 0), rh=(42, 0, 6), lh=(-32, 0, -6), d=(0, -0.2, 0))),
        ('Back', P(S0, root=(16, 0, 0), rs=(64, 0, 12), ls=(60, 0, -8), neck=(-10, 0, 0), rh=(-12, 0, 6), lh=(32, 0, -6), d=(0, -0.2, 0))),
        ('Left', P(S0, root=(-6, 10, 22), rs=(10, 0, 30), ls=(10, 0, -52), neck=(0, -8, -18), rh=(0, 0, 22), lh=(0, 0, -28), d=(-0.2, -0.2, 0))),
        ('Right', P(S0, root=(-6, -10, -22), rs=(10, 0, 52), ls=(10, 0, -30), neck=(0, 8, 18), rh=(0, 0, 28), lh=(0, 0, -22), d=(0.2, -0.2, 0)))):
    add(f'Sword_Dash{dname}', [(0, S0, 'cubic'), (3, pose, 'out'), (9, P(pose), 'constant'), (14, S0, 'cubic')],
        priority='Action', notes=f'Dash {dname.lower()} (movement itself is done by game code).')

# ================================================================================================= FISTS
add('Fist_Idle', [(0, F0, 'cubic'), (20, P(F0, d=(0, -0.24, 0), rs=(80, 0, -24), ls=(86, 0, 24)), 'cubic'), (40, F0, 'cubic')],
    loop=True, priority='Idle', notes='Boxing guard with a bounce.')
add('Fist_Combo1', [
    (0, F0, 'cubic'), (2, P(F0, root=(-8, -6, 0)), 'cubic'),
    (4, P(F0, ls=(96, 0, 4), root=(-12, 12, 0), neck=(-4, -8, 0), **legs_for_yaw(12)), 'out'),
    (7, P(F0, ls=(99, 0, 2), root=(-13, 14, 0), **legs_for_yaw(14)), 'out'), (12, F0, 'cubic')], markers={'Hit': 4}, notes='Left jab.')
add('Fist_Combo2', [
    (0, F0, 'cubic'), (3, P(F0, root=(-8, -32, 0), rs=(70, 0, -30), **legs_for_yaw(-32)), 'cubic'),
    (5, P(F0, rs=(96, 0, -4), root=(-15, 36, 0), ls=(70, 0, 30), neck=(-4, -30, 0), **legs_for_yaw(36)), 'out'),
    (8, P(F0, rs=(99, 0, -2), root=(-16, 40, 0), neck=(-4, -34, 0), **legs_for_yaw(40)), 'out'), (14, F0, 'cubic')],
    markers={'Hit': 5}, notes='Right cross.')
add('Fist_Combo3', [
    (0, F0, 'cubic'), (4, P(F0, root=(-8, -36, 0), ls=(88, 0, -48), **legs_for_yaw(-36)), 'cubic'),
    (7, P(F0, root=(-10, 40, 0), ls=(90, 0, 44), neck=(-4, -34, 0), **legs_for_yaw(40)), 'out'),
    (10, P(F0, root=(-10, 48, 0), ls=(88, 0, 52), neck=(-4, -40, 0), **legs_for_yaw(48)), 'out'), (16, F0, 'cubic')],
    markers={'Hit': 7}, notes='Left hook.')
add('Fist_Combo4', [
    (0, F0, 'cubic'), (5, P(F0, rh=(82, 10, 28), root=(10, 22, 0), lh=(-6, -22, -6)), 'cubic'),
    (10, P(F0, rh=(86, 0, 72), root=(16, 62, 0), lh=(-4, -62, -8), neck=(0, -50, 0), rs=(70, 0, -40), ls=(88, 0, 30)), 'out'),
    (14, P(F0, rh=(84, 0, 80), root=(18, 70, 0), lh=(-4, -70, -8), neck=(0, -56, 0)), 'out'),
    (22, F0, 'cubic')], markers={'Hit': 10}, notes='Right roundhouse kick finisher.')
_fb = P(F0, rs=(102, 0, -46), ls=(102, 0, 46), root=(-15, 0, 0), neck=(-12, 0, 0), d=(0, -0.22, 0), rh=(12, 0, 6), lh=(-12, 0, -6))
add('Fist_Block', [(0, _fb, 'cubic'), (10, P(_fb, d=(0, -0.26, 0)), 'cubic'), (20, _fb, 'cubic')], loop=True, notes='Forearms crossed before the face.')

# ================================================================================================= MOVEMENT
_run_a = dict(root=(-15, 4, 0), neck=(10, -4, 0), rs=(-55, 0, 6), ls=(62, 0, -6), rh=(52, -4, 2), lh=(-46, -4, -2), d=(0, -0.1, 0))
_run_p = dict(root=(-13, 0, 0), neck=(9, 0, 0), rs=(4, 0, 6), ls=(4, 0, -6), rh=(8, 0, 2), lh=(-6, 0, -2), d=(0, 0.1, 0))
add('Run', [(0, _run_a, 'cubic'), (5, _run_p, 'cubic'), (10, mirror(_run_a), 'cubic'), (15, mirror(_run_p), 'cubic'), (20, _run_a, 'cubic')],
    loop=True, priority='Movement', notes='Anime sprint: forward lean, big arm swing.')
add('Jump', [
    (0, N, 'cubic'),
    (3, P(N, root=(-16, 0, 0), rs=(-42, 0, 10), ls=(-42, 0, -10), rh=(40, 0, 2), lh=(-36, 0, -2), d=(0, -0.42, 0)), 'cubic'),
    (7, P(N, root=(6, 0, 0), rs=(150, 0, 16), ls=(150, 0, -16), rh=(-6, 0, 2), lh=(-16, 0, -2), neck=(10, 0, 0), d=(0, 0.1, 0)), 'out'),
    (14, AIR, 'cubic')], priority='Movement', notes='Crouch, launch (arms up), settle into the airborne pose.')
_tuck = dict(root=(-90, 0, 0), neck=(-20, 0, 0), rs=(62, 0, -22), ls=(62, 0, 22), rh=(112, 0, 6), lh=(112, 0, -6), d=(0, 0.5, 0))
add('DoubleJump', [
    (0, AIR, 'cubic'), (4, _tuck, 'out'), (8, P(_tuck, root=(-200, 0, 0)), 'linear'), (13, P(_tuck, root=(-300, 0, 0)), 'linear'),
    (17, P(AIR, root=(-362, 0, 0), rs=(20, 0, 62), ls=(20, 0, -62), rh=(12, 0, 4), lh=(-6, 0, -4)), 'out'),
    (24, P(AIR, root=(-360, 0, 0)), 'cubic')], priority='Action', notes='Tucked front flip (full 360 torso rotation about the root).')
add('Landing', [
    (0, AIR, 'cubic'),
    (3, P(N, root=(-22, 0, 0), rs=(32, 0, 40), ls=(32, 0, -40), rh=(46, 0, 8), lh=(-46, 0, -8), neck=(12, 0, 0), d=(0, -0.62, 0)), 'out'),
    (12, N, 'cubic')], priority='Movement', notes='Impact crouch (legs spread to keep the feet on the ground) and recover.')

# ================================================================================================= SKILL CASTS
add('Cast_Projectile', [
    (0, N, 'cubic'),
    (5, P(N, root=(6, -36, 0), rs=(-52, 0, 32), ls=(62, 0, 22), neck=(-4, 32, 0), **legs_for_yaw(-36)), 'cubic'),
    (9, P(N, root=(-15, 36, 0), rs=(102, 0, -10), ls=(-20, 0, -10), neck=(-6, -32, 0), d=(0, -0.12, 0), **legs_for_yaw(36)), 'out'),
    (13, P(N, root=(-20, 46, 0), rs=(82, 0, -30), ls=(-24, 0, -14), neck=(-8, -40, 0), d=(0, -0.16, 0), **legs_for_yaw(46)), 'out'),
    (20, N, 'cubic')], markers={'Hit': 9}, notes='Wind-up and throw; Hit = release frame (spawn the projectile).')
_beam = P(N, rs=(90, 5, -8), ls=(90, -5, 8), root=(-10, 0, 0), neck=(-4, 0, 0), rh=(16, 0, 8), lh=(-16, 0, -8), d=(0, -0.2, 0))
add('Cast_BeamChannel', [
    (0, _beam, 'cubic'), (6, P(_beam, rs=(92, 6, -7), ls=(88, -4, 9), root=(-12, 1, 0)), 'linear'),
    (12, P(_beam, rs=(89, 4, -9), ls=(91, -6, 7), root=(-9, -1, 0), d=(0, -0.24, 0)), 'linear'),
    (18, P(_beam, rs=(91, 5, -8), ls=(90, -5, 8), root=(-11, 0, 0)), 'linear'), (24, _beam, 'linear')],
    loop=True, priority='Action', markers={'Hit': 0}, notes='Two-handed beam channel (loop); Hit at 0 = beam start.')
_slam = P(N, root=(-46, 0, 0), rs=(38, 0, 10), ls=(38, 0, -10), neck=(20, 0, 0), rh=(52, 0, 6), lh=(-40, 0, -6), d=(0, -0.92, 0))
add('Cast_GroundSlam', [
    (0, N, 'cubic'),
    (8, P(N, rs=(170, 0, 14), ls=(170, 0, -14), root=(10, 0, 0), neck=(12, 0, 0), d=(0, 0.3, 0)), 'cubic'),
    (12, P(N, rs=(176, 0, 12), ls=(176, 0, -12), root=(12, 0, 0), neck=(14, 0, 0), d=(0, 0.34, 0)), 'cubic'),
    (16, _slam, 'in'), (22, P(_slam), 'constant'), (30, N, 'cubic')], markers={'Hit': 16},
    notes='Raise both fists and slam the ground; Hit = impact (spawn shockwave / rock shards).')
_summon = P(N, rs=(170, 0, 36), ls=(170, 0, -36), root=(12, 0, 0), neck=(26, 0, 0), d=(0, 0.1, 0))
add('Cast_Summon', [
    (0, N, 'cubic'), (8, P(N, rs=(22, 0, -42), ls=(22, 0, 42), root=(-12, 0, 0), neck=(-12, 0, 0), d=(0, -0.24, 0)), 'cubic'),
    (16, _summon, 'out'), (18, P(_summon, rs=(172, 0, 38), ls=(172, 0, -38)), 'out'), (30, P(_summon), 'constant'), (36, N, 'cubic')],
    markers={'Hit': 18}, notes='Gather low, then arms raised to summon; Hit = summon moment.')
add('Cast_GrabThrow', [
    (0, N, 'cubic'),
    (5, P(N, rs=(96, 0, 0), root=(-20, 10, 0), neck=(-6, -8, 0), **legs_for_yaw(10, fwd=30, back=-24)), 'cubic'),
    (8, P(N, rs=(90, 0, -6), root=(-18, 10, 0), **legs_for_yaw(10, fwd=30, back=-24)), 'out'),
    (14, P(N, rs=(160, 0, 12), root=(10, -30, 0), neck=(8, 26, 0), ls=(40, 0, -30), **legs_for_yaw(-30)), 'cubic'),
    (20, P(N, rs=(150, 0, 62), root=(6, -70, 0), neck=(4, 60, 0), ls=(30, 0, -40), **legs_for_yaw(-70)), 'cubic'),
    (24, P(N, rs=(70, 0, -40), root=(-20, 50, 0), neck=(-8, -44, 0), ls=(-10, 0, -20), d=(0, -0.2, 0), **legs_for_yaw(50)), 'out'),
    (34, N, 'cubic')], markers={'Hit': 8, 'Hit2': 24}, notes='Grab (Hit = catch), lift, spin, throw (Hit2 = release).')

# ================================================================================================= EARTH GOLEM (Golem rig)
G0 = dict(root=(-8, 0, 0), neck=(6, 0, 0), rs=(16, 0, 14), ls=(16, 0, -14), rh=(4, 0, 8), lh=(4, 0, -8), d=(0, -0.05, 0))
_gw = P(G0, rh=(24, 0, 8), lh=(-20, 0, -8), root=(-8, 6, 5), rs=(-14, 0, 14), ls=(30, 0, -14), d=(0, -0.08, 0))
_gp = P(G0, rh=(2, 0, 8), lh=(2, 0, -8), root=(-9, 0, 0), d=(0, 0.06, 0))
add('Golem_Walk', [(0, _gw, 'cubic'), (12, _gp, 'cubic'), (24, mirror(_gw), 'cubic'), (36, _gp, 'cubic'), (48, _gw, 'cubic')],
    loop=True, priority='Movement', rig=GOLEM, notes='Heavy, swaying walk.')
_gpw = P(G0, root=(-6, -36, 0), rs=(-40, 0, 30), ls=(40, 0, -20), neck=(0, 30, 0), **legs_for_yaw(-36, 10, -8, 10))
_gps = P(G0, root=(-20, 30, 0), rs=(96, 0, -10), ls=(-10, 0, -20), neck=(-6, -26, 0), d=(0, -0.2, 0), **legs_for_yaw(30, 22, -18, 10))
add('Golem_Punch1', [(0, G0, 'cubic'), (10, _gpw, 'cubic'), (15, _gps, 'out'), (20, P(_gps, rs=(99, 0, -12)), 'out'), (30, G0, 'cubic')],
    markers={'Hit': 15}, rig=GOLEM, notes='Right straight punch.')
add('Golem_Punch2', [(0, G0, 'cubic'), (10, mirror(_gpw), 'cubic'), (15, mirror(_gps), 'out'), (20, mirror(P(_gps, rs=(99, 0, -12))), 'out'), (30, G0, 'cubic')],
    markers={'Hit': 15}, rig=GOLEM, notes='Left straight punch.')
add('Golem_Punch3', [
    (0, G0, 'cubic'), (10, P(G0, root=(-24, -22, 0), rs=(-22, 0, 22), d=(0, -0.42, 0), rh=(30, 22, 10), lh=(-26, 22, -10)), 'cubic'),
    (16, P(G0, root=(10, 16, 0), rs=(162, 0, -6), neck=(14, -10, 0), d=(0, 0.08, 0), rh=(8, -16, 10), lh=(-8, -16, -10)), 'out'),
    (22, P(G0, root=(12, 18, 0), rs=(168, 0, -4), neck=(16, -12, 0), rh=(8, -18, 10), lh=(-8, -18, -10)), 'out'), (34, G0, 'cubic')],
    markers={'Hit': 16}, rig=GOLEM, notes='Right uppercut (3rd hit).')
_gsl = P(G0, rs=(30, 0, 6), ls=(30, 0, -6), root=(-50, 0, 0), neck=(26, 0, 0), d=(0, -1.0, 0), rh=(42, 0, 10), lh=(-40, 0, -10))
add('Golem_Slam', [
    (0, G0, 'cubic'), (14, P(G0, rs=(176, 0, 10), ls=(176, 0, -10), root=(15, 0, 0), neck=(14, 0, 0), d=(0, 0.4, 0)), 'cubic'),
    (18, P(G0, rs=(178, 0, 8), ls=(178, 0, -8), root=(17, 0, 0), neck=(15, 0, 0), d=(0, 0.44, 0)), 'cubic'),
    (22, _gsl, 'in'), (32, P(_gsl), 'constant'), (44, G0, 'cubic')], markers={'Hit': 22}, rig=GOLEM,
    notes='Two-handed overhead slam; Hit = impact.')
_gland = P(G0, rs=(30, 0, 20), ls=(30, 0, -20), root=(-40, 0, 0), neck=(20, 0, 0), d=(0, -1.1, 0), rh=(50, 0, 12), lh=(-50, 0, -12))
add('Golem_LeapSmash', [
    (0, G0, 'cubic'), (12, P(G0, d=(0, -0.9, 0), rh=(50, 0, 10), lh=(-46, 0, -10), rs=(-40, 0, 20), ls=(-40, 0, -20), root=(-20, 0, 0)), 'cubic'),
    (20, P(G0, rs=(150, 0, 20), ls=(150, 0, -20), rh=(70, 0, 8), lh=(62, 0, -8), root=(-10, 0, 0), d=(0, 0.6, 0)), 'out'),
    (32, P(G0, rs=(160, 0, 14), ls=(160, 0, -14), rh=(80, 0, 8), lh=(74, 0, -8), root=(-4, 0, 0), d=(0, 0.6, 0)), 'cubic'),
    (38, _gland, 'in'), (50, P(_gland), 'constant'), (60, G0, 'cubic')], markers={'Hit': 38}, rig=GOLEM,
    notes='Crouch, leap (tuck), landing smash; Hit = landing impact (game moves the root).')
_roar = P(G0, root=(26, 0, 0), neck=(32, 0, 0), rs=(-22, 0, 72), ls=(-22, 0, -72), d=(0, 0.1, 0))
add('Golem_Roar', [
    (0, G0, 'cubic'), (10, P(G0, root=(-26, 0, 0), rs=(40, 0, 22), ls=(40, 0, -22), neck=(-10, 0, 0), d=(0, -0.3, 0)), 'cubic'),
    (18, _roar, 'out'), (22, P(_roar, root=(24, 2, 1)), 'linear'), (26, P(_roar, root=(27, -2, -1)), 'linear'),
    (30, P(_roar, root=(25, 2, 1)), 'linear'), (34, P(_roar, root=(26, -1, 0)), 'linear'), (40, P(_roar), 'linear'), (50, G0, 'cubic')],
    markers={'Hit': 18}, rig=GOLEM, notes='Gather and roar with body shake; Hit = roar start (screen shake / VFX).')

# ================================================================================================= THE HOLLOW (R6)
H0 = dict(root=(-34, 0, 0), neck=(32, 0, 0), rs=(36, 0, 10), ls=(30, 0, -12), rh=(40, 0, 10), lh=(28, 0, -10), d=(0, -0.42, 0))
add('Hollow_Idle', [
    (0, H0, 'cubic'), (6, P(H0, neck=(28, 24, 16)), 'linear'), (8, H0, 'linear'), (20, P(H0, rs=(48, 0, 22)), 'linear'),
    (22, H0, 'linear'), (30, P(H0, neck=(20, -30, -22)), 'linear'), (33, H0, 'linear'), (40, P(H0, d=(0, -0.48, 0), root=(-37, 0, 0)), 'cubic'),
    (48, H0, 'cubic')], loop=True, priority='Idle', notes='Hunched, breathing, sudden twitches.')
_hs = P(H0, rh=(58, 4, 10), lh=(14, 4, -10), rs=(20, 0, 12), ls=(48, 0, -12), root=(-34, 8, 3), neck=(30, -8, 8))
add('Hollow_Stalk', [(0, _hs, 'cubic'), (8, P(H0, d=(0, -0.36, 0)), 'cubic'), (16, mirror(_hs), 'cubic'), (24, P(H0, d=(0, -0.36, 0)), 'cubic'),
                     (32, _hs, 'cubic')], loop=True, priority='Movement', notes='Hunched stalking walk.')
add('Hollow_Lunge', [
    (0, H0, 'cubic'), (6, P(H0, d=(0, -0.8, 0), root=(-46, 0, 0), rs=(-30, 0, 20), ls=(-30, 0, -20), rh=(56, 0, 10), lh=(46, 0, -10)), 'cubic'),
    (10, P(H0, root=(-62, 0, 0), rs=(112, 0, 16), ls=(112, 0, -16), neck=(46, 0, 0), rh=(20, 0, 8), lh=(72, 0, -8), d=(0, -0.2, 0)), 'out'),
    (14, P(H0, root=(-66, 0, 0), rs=(96, 0, -8), ls=(96, 0, 8), neck=(48, 0, 0), rh=(24, 0, 8), lh=(70, 0, -8), d=(0, -0.3, 0)), 'out'),
    (22, H0, 'cubic')], markers={'Hit': 10}, notes='Coiled lunge with both claws; Hit = claws connect.')
add('Hollow_HitReaction', [
    (0, H0, 'cubic'), (2, P(H0, root=(-6, 0, 10), neck=(52, 20, 0), rs=(62, 0, 52), ls=(62, 0, -52), d=(0, -0.22, 0)), 'out'),
    (6, P(H0, root=(-12, 0, 6), neck=(46, 14, 0), rs=(54, 0, 44), ls=(54, 0, -44)), 'cubic'), (14, H0, 'cubic')],
    priority='Action2', notes='Snapped back by a hit.')
add('Hollow_Death', [
    (0, H0, 'cubic'), (6, P(H0, root=(-6, 20, 16), neck=(44, 20, 10), rs=(60, 0, 50), ls=(40, 0, -60)), 'out'),
    (16, P(H0, d=(0, -1.6, 0), root=(-20, 10, 4), rh=(90, 0, 8), lh=(88, 0, -8), rs=(10, 0, 20), ls=(10, 0, -20), neck=(10, 0, 0)), 'in'),
    (26, P(H0, root=(-86, 0, 0), d=(0, -2.3, 0), rs=(160, 0, 12), ls=(156, 0, -10), rh=(96, 0, 6), lh=(94, 0, -6), neck=(40, 10, 0)), 'in'),
    (50, P(H0, root=(-88, 0, 0), d=(0, -2.35, 0), rs=(162, 0, 12), ls=(158, 0, -10), rh=(96, 0, 6), lh=(94, 0, -6), neck=(40, 10, 0)), 'cubic')],
    priority='Action4', notes='Stagger, fall to the knees, collapse face down (ends lying; keep the last frame).')

# ================================================================================================= PAIRED FINISHERS
# Victim starts 5 studs in front of the attacker (attacker HRP * CFrame.new(0, 0, -5) * CFrame.Angles(0, pi, 0)), facing the attacker.
_imp = P(S0, root=(-26, 5, 0), rs=(90, 0, -4), ls=(70, 0, 20), neck=(-8, -5, 0), d=(0, -0.3, 0), rh=(42, -5, 6), lh=(-36, -5, -6))
add('Finisher_OathCut_Attacker', [
    (0, S0, 'cubic'), (10, P(S0, root=(-10, -42, 0), rs=(40, 0, 62), d=(0, -0.32, 0), **legs_for_yaw(-42)), 'cubic'),
    (16, _imp, 'out'), (40, P(_imp, d=(0, -0.34, 0)), 'constant'),
    (46, P(_imp, root=(-25, 26, 0), rs=(92, 10, -20), **legs_for_yaw(26, 42, -36)), 'out'),
    (56, P(S0, rs=(132, 0, 52), root=(-5, -52, 0), neck=(4, 44, 0), **legs_for_yaw(-52)), 'out'),
    (70, P(S0, rs=(20, 0, -30), ls=(10, 0, 10), root=(0, -20, 0), neck=(-10, 18, 0)), 'cubic'),
    (90, S0, 'cubic')], markers={'Hit': 16, 'Hit2': 46, 'Hit3': 56}, priority='Action4',
    notes='Paired with Finisher_OathCut_Victim (victim 5 studs in front, facing the attacker). Stab (held), twist, rip-out slash.')
_bent = P(N, root=(-32, 0, 0), rs=(42, 0, -22), ls=(42, 0, 22), neck=(-22, 0, 0), d=(0, -0.3, 0), rh=(34, 0, 4), lh=(26, 0, -4))
add('Finisher_OathCut_Victim', [
    (0, N, 'cubic'), (16, _bent, 'out'), (28, P(_bent, root=(-34, 2, 0)), 'linear'), (40, P(_bent, root=(-31, -2, 0)), 'linear'),
    (46, P(_bent, root=(-42, 12, 0)), 'out'), (56, P(N, root=(10, 40, -20), rs=(60, 0, 50), ls=(20, 0, -60), neck=(30, 10, 0)), 'out'),
    (66, P(N, d=(0, -1.6, 0), root=(-20, 20, 0), rh=(90, 0, 6), lh=(88, 0, -6), rs=(10, 0, 10), ls=(10, 0, -10)), 'in'),
    (78, P(N, root=(-86, 20, 0), d=(0, -2.3, 0), rs=(150, 0, 20), ls=(150, 0, -20), rh=(96, 0, 4), lh=(94, 0, -4)), 'in'),
    (90, P(N, root=(-88, 20, 0), d=(0, -2.35, 0), rs=(152, 0, 20), ls=(152, 0, -20), rh=(96, 0, 4), lh=(94, 0, -4)), 'cubic')],
    markers={'Hit': 16, 'Hit2': 46, 'Hit3': 56}, priority='Action4', notes='Paired victim of OathCut; ends lying face down.')
_down = P(S0, rs=(40, 0, 0), ls=(36, 0, 14), root=(-40, 0, 0), neck=(-16, 0, 0), d=(0, -0.6, 0), rh=(44, 0, 6), lh=(-38, 0, -6))
add('Finisher_TwinDraw_Attacker', [
    (0, S0, 'cubic'), (8, P(S0, rh=(82, 0, 10), root=(6, 0, 0)), 'cubic'), (12, P(S0, rh=(150, 0, 4), root=(16, 0, 0), neck=(8, 0, 0)), 'out'),
    (20, P(S0, d=(0, -0.5, 0), rh=(40, 20, 6), lh=(-36, 20, -6), root=(-18, -20, 0)), 'cubic'),
    (28, P(AIR, rs=(132, 0, 62), root=(-6, -30, 0)), 'out'), (34, P(AIR, rs=(40, 0, -62), root=(-10, 40, 0)), 'out'),
    (44, P(AIR, rs=(176, 0, 8), ls=(160, 0, -10), root=(8, 0, 0), neck=(10, 0, 0)), 'cubic'),
    (52, _down, 'in'), (70, P(_down, d=(0, -0.64, 0)), 'constant'), (85, P(S0, rs=(20, 0, -20)), 'cubic'), (105, S0, 'cubic')],
    markers={'Hit': 12, 'Hit2': 34, 'Hit3': 52}, priority='Action4',
    notes='Paired with Finisher_TwinDraw_Victim: launching kick, aerial slash, downward finishing cut held (game moves roots).')
add('Finisher_TwinDraw_Victim', [
    (0, N, 'cubic'), (12, P(N, root=(36, 0, 0), rs=(150, 0, 30), ls=(150, 0, -30), neck=(30, 0, 0), rh=(-20, 0, 6), lh=(10, 0, -6)), 'out'),
    (30, P(N, root=(-60, 0, 0), rs=(90, 0, 60), ls=(90, 0, -60), rh=(60, 0, 10), lh=(40, 0, -10)), 'cubic'),
    (34, P(N, root=(-120, 0, 10), rs=(120, 0, 70), ls=(100, 0, -70), rh=(80, 0, 10), lh=(50, 0, -10)), 'out'),
    (52, P(N, root=(-88, 0, 0), d=(0, -2.3, 0), rs=(150, 0, 20), ls=(150, 0, -20), rh=(96, 0, 4), lh=(94, 0, -4)), 'in'),
    (105, P(N, root=(-89, 0, 0), d=(0, -2.35, 0), rs=(152, 0, 20), ls=(152, 0, -20), rh=(96, 0, 4), lh=(94, 0, -4)), 'cubic')],
    markers={'Hit': 12, 'Hit2': 34, 'Hit3': 52}, priority='Action4', notes='Launched, cut in the air, slammed down; ends lying.')
