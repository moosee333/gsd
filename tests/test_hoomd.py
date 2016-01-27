# Copyright (c) 2016 The Regents of the University of Michigan
# This file is part of the General Simulation Data (GSD) project, released under the BSD 2-Clause License.

import gsd.fl
import gsd.hoomd
import tempfile
import numpy
from nose.tools import ok_, eq_, assert_raises

def test_create():
    with tempfile.TemporaryDirectory() as d:
        gsd.hoomd.create(name=d+"/test_create.gsd", snapshot=None);

        with gsd.fl.GSDFile(name=d+"/test_create.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            eq_(f.schema, 'hoomd');
            ok_(f.schema_version >= (0,1));

def test_append():
    with tempfile.TemporaryDirectory() as d:
        snap = gsd.hoomd.Snapshot();
        snap.particles.N = 10;
        gsd.hoomd.create(name=d+"/test_append.gsd", snapshot=snap);

        with gsd.fl.GSDFile(name=d+"/test_append.gsd", mode='w') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            for i in range(5):
                snap.configuration.step=i+1;
                hf.append(snap);

        with gsd.fl.GSDFile(name=d+"/test_append.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            eq_(len(hf), 6);

def create_frame(i):
    snap = gsd.hoomd.Snapshot();
    snap.configuration.step = i+1;
    return snap

def test_extend():
    with tempfile.TemporaryDirectory() as d:
        snap = gsd.hoomd.Snapshot();
        snap.particles.N = 10;
        gsd.hoomd.create(name=d+"/test_extend.gsd", snapshot=snap);

        with gsd.fl.GSDFile(name=d+"/test_extend.gsd", mode='w') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            hf.extend((create_frame(i) for i in range(5)));

        with gsd.fl.GSDFile(name=d+"/test_extend.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            eq_(len(hf), 6);

def test_defaults():
    with tempfile.TemporaryDirectory() as d:
        snap = gsd.hoomd.Snapshot();
        snap.particles.N = 2;
        snap.bonds.N = 3;
        snap.angles.N = 4;
        snap.dihedrals.N = 5;
        snap.impropers.N = 6;
        gsd.hoomd.create(name=d+"/test_defaults.gsd", snapshot=snap);

        with gsd.fl.GSDFile(name=d+"/test_defaults.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            s = hf.read_frame(0);

            eq_(s.configuration.step, 0);
            eq_(s.configuration.dimensions, 3);
            numpy.testing.assert_array_equal(s.configuration.box, numpy.array([1,1,1,0,0,0], dtype=numpy.float32));
            eq_(s.particles.N, 2);
            eq_(s.particles.types, ['A']);
            numpy.testing.assert_array_equal(s.particles.typeid, numpy.array([0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.particles.mass, numpy.array([1,1], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.diameter, numpy.array([1,1], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.charge, numpy.array([0,0], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.moment_inertia, numpy.array([[0,0,0],[0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.position, numpy.array([[0,0,0],[0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.orientation, numpy.array([[1,0,0,0],[1,0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.velocity, numpy.array([[0,0,0],[0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.angmom, numpy.array([[0,0,0,0],[0,0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.image, numpy.array([[0,0,0],[0,0,0]], dtype=numpy.int32));

            eq_(s.bonds.N, 3);
            eq_(s.bonds.types, []);
            numpy.testing.assert_array_equal(s.bonds.typeid, numpy.array([0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.bonds.group, numpy.array([[0,0],[0,0],[0,0]], dtype=numpy.uint32));

            eq_(s.angles.N, 4);
            eq_(s.angles.types, []);
            numpy.testing.assert_array_equal(s.angles.typeid, numpy.array([0,0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.angles.group, numpy.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0]], dtype=numpy.uint32));

            eq_(s.dihedrals.N, 5);
            eq_(s.dihedrals.types, []);
            numpy.testing.assert_array_equal(s.dihedrals.typeid, numpy.array([0,0,0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.dihedrals.group, numpy.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=numpy.uint32));

            eq_(s.impropers.N, 6);
            eq_(s.impropers.types, []);
            numpy.testing.assert_array_equal(s.impropers.typeid, numpy.array([0,0,0,0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.impropers.group, numpy.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=numpy.uint32));

def test_fallback():
    with tempfile.TemporaryDirectory() as d:
        snap0 = gsd.hoomd.Snapshot();
        snap0.configuration.step = 10000;
        snap0.configuration.dimensions = 2;
        snap0.configuration.box = [4,5,6,1.0,0.5,0.25];
        snap0.particles.N = 2;
        snap0.particles.types = ['A', 'B', 'C']
        snap0.particles.typeid = [1,2];
        snap0.particles.mass = [2,3];
        snap0.particles.diameter = [3,4];
        snap0.particles.charge = [0.5, 0.25];
        snap0.particles.moment_inertia = [[1,2,3], [3,2,1]];
        snap0.particles.position = [[0.1, 0.2, 0.3], [-1.0, -2.0, -3.0]];
        snap0.particles.orientation = [[1, 0.1, 0.2, 0.3], [0, -1.0, -2.0, -3.0]];
        snap0.particles.velocity = [[1.1, 2.2, 3.3], [-3.3, -2.2, -1.1]];
        snap0.particles.angmom = [[1, 1.1, 2.2, 3.3], [-1, -3.3, -2.2, -1.1]];
        snap0.particles.image = [[10, 20, 30], [5, 6, 7]];

        snap0.bonds.N = 1;
        snap0.bonds.types = ['bondA', 'bondB']
        snap0.bonds.typeid = [1];
        snap0.bonds.group = [[0,1]];

        snap0.angles.N = 1;
        snap0.angles.typeid = [2];
        snap0.angles.types = ['angleA', 'angleB']
        snap0.angles.group = [[0,1, 0]];

        snap0.dihedrals.N = 1;
        snap0.dihedrals.typeid = [3];
        snap0.dihedrals.types = ['dihedralA', 'dihedralB']
        snap0.dihedrals.group = [[0,1, 1, 0]];

        snap0.impropers.N = 1;
        snap0.impropers.typeid = [4];
        snap0.impropers.types = ['improperA', 'improperB']
        snap0.impropers.group = [[1, 0, 0, 1]];

        snap1 = gsd.hoomd.Snapshot();
        snap1.particles.N = 2;
        snap1.particles.position = [[-2, -1, 0], [1, 3.0, 0.5]];

        snap2 = gsd.hoomd.Snapshot();
        snap2.particles.N = 3;
        snap2.particles.types = ['q', 's'];
        snap2.bonds.N = 3;
        snap2.angles.N = 4;
        snap2.dihedrals.N = 5;
        snap2.impropers.N = 6;

        gsd.hoomd.create(name=d+"/test_fallback.gsd");

        with gsd.fl.GSDFile(name=d+"/test_fallback.gsd", mode='w') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            hf.extend([snap0, snap1, snap2]);

        with gsd.fl.GSDFile(name=d+"/test_fallback.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            eq_(len(hf), 3);
            s = hf.read_frame(0);

            eq_(s.configuration.step, snap0.configuration.step);
            eq_(s.configuration.dimensions, snap0.configuration.dimensions);
            numpy.testing.assert_array_equal(s.configuration.box, snap0.configuration.box);
            eq_(s.particles.N, snap0.particles.N);
            eq_(s.particles.types, snap0.particles.types);
            numpy.testing.assert_array_equal(s.particles.typeid, snap0.particles.typeid);
            numpy.testing.assert_array_equal(s.particles.mass, snap0.particles.mass);
            numpy.testing.assert_array_equal(s.particles.diameter, snap0.particles.diameter);
            numpy.testing.assert_array_equal(s.particles.charge, snap0.particles.charge);
            numpy.testing.assert_array_equal(s.particles.moment_inertia, snap0.particles.moment_inertia);
            numpy.testing.assert_array_equal(s.particles.position, snap0.particles.position);
            numpy.testing.assert_array_equal(s.particles.orientation, snap0.particles.orientation);
            numpy.testing.assert_array_equal(s.particles.velocity, snap0.particles.velocity);
            numpy.testing.assert_array_equal(s.particles.angmom, snap0.particles.angmom);
            numpy.testing.assert_array_equal(s.particles.image, snap0.particles.image);

            eq_(s.bonds.N, snap0.bonds.N);
            eq_(s.bonds.types, snap0.bonds.types);
            numpy.testing.assert_array_equal(s.bonds.typeid, snap0.bonds.typeid);
            numpy.testing.assert_array_equal(s.bonds.group, snap0.bonds.group);

            eq_(s.angles.N, snap0.angles.N);
            eq_(s.angles.types, snap0.angles.types);
            numpy.testing.assert_array_equal(s.angles.typeid, snap0.angles.typeid);
            numpy.testing.assert_array_equal(s.angles.group, snap0.angles.group);

            eq_(s.dihedrals.N, snap0.dihedrals.N);
            eq_(s.dihedrals.types, snap0.dihedrals.types);
            numpy.testing.assert_array_equal(s.dihedrals.typeid, snap0.dihedrals.typeid);
            numpy.testing.assert_array_equal(s.dihedrals.group, snap0.dihedrals.group);

            eq_(s.impropers.N, snap0.impropers.N);
            eq_(s.impropers.types, snap0.impropers.types);
            numpy.testing.assert_array_equal(s.impropers.typeid, snap0.impropers.typeid);
            numpy.testing.assert_array_equal(s.impropers.group, snap0.impropers.group);

            # test that everything but position remained the same in frame 1
            s = hf.read_frame(1);

            eq_(s.configuration.step, snap0.configuration.step);
            eq_(s.configuration.dimensions, snap0.configuration.dimensions);
            numpy.testing.assert_array_equal(s.configuration.box, snap0.configuration.box);
            eq_(s.particles.N, snap0.particles.N);
            eq_(s.particles.types, snap0.particles.types);
            numpy.testing.assert_array_equal(s.particles.typeid, snap0.particles.typeid);
            numpy.testing.assert_array_equal(s.particles.mass, snap0.particles.mass);
            numpy.testing.assert_array_equal(s.particles.diameter, snap0.particles.diameter);
            numpy.testing.assert_array_equal(s.particles.charge, snap0.particles.charge);
            numpy.testing.assert_array_equal(s.particles.moment_inertia, snap0.particles.moment_inertia);
            numpy.testing.assert_array_equal(s.particles.position, snap1.particles.position);
            numpy.testing.assert_array_equal(s.particles.orientation, snap0.particles.orientation);
            numpy.testing.assert_array_equal(s.particles.velocity, snap0.particles.velocity);
            numpy.testing.assert_array_equal(s.particles.angmom, snap0.particles.angmom);
            numpy.testing.assert_array_equal(s.particles.image, snap0.particles.image);

            eq_(s.bonds.N, snap0.bonds.N);
            eq_(s.bonds.types, snap0.bonds.types);
            numpy.testing.assert_array_equal(s.bonds.typeid, snap0.bonds.typeid);
            numpy.testing.assert_array_equal(s.bonds.group, snap0.bonds.group);

            eq_(s.angles.N, snap0.angles.N);
            eq_(s.angles.types, snap0.angles.types);
            numpy.testing.assert_array_equal(s.angles.typeid, snap0.angles.typeid);
            numpy.testing.assert_array_equal(s.angles.group, snap0.angles.group);

            eq_(s.dihedrals.N, snap0.dihedrals.N);
            eq_(s.dihedrals.types, snap0.dihedrals.types);
            numpy.testing.assert_array_equal(s.dihedrals.typeid, snap0.dihedrals.typeid);
            numpy.testing.assert_array_equal(s.dihedrals.group, snap0.dihedrals.group);

            eq_(s.impropers.N, snap0.impropers.N);
            eq_(s.impropers.types, snap0.impropers.types);
            numpy.testing.assert_array_equal(s.impropers.typeid, snap0.impropers.typeid);
            numpy.testing.assert_array_equal(s.impropers.group, snap0.impropers.group);

            # check that the third frame goes back to defaults because it has a different N
            s = hf.read_frame(2);

            eq_(s.particles.N, 3);
            eq_(s.particles.types, ['q', 's']);
            numpy.testing.assert_array_equal(s.particles.typeid, numpy.array([0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.particles.mass, numpy.array([1,1,1], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.diameter, numpy.array([1,1,1], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.charge, numpy.array([0,0,0], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.moment_inertia, numpy.array([[0,0,0],[0,0,0],[0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.position, numpy.array([[0,0,0],[0,0,0],[0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.orientation, numpy.array([[1,0,0,0],[1,0,0,0],[1,0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.velocity, numpy.array([[0,0,0],[0,0,0],[0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.angmom, numpy.array([[0,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=numpy.float32));
            numpy.testing.assert_array_equal(s.particles.image, numpy.array([[0,0,0],[0,0,0],[0,0,0]], dtype=numpy.int32));

            eq_(s.bonds.N, 3);
            eq_(s.bonds.types, snap0.bonds.types);
            numpy.testing.assert_array_equal(s.bonds.typeid, numpy.array([0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.bonds.group, numpy.array([[0,0],[0,0],[0,0]], dtype=numpy.uint32));

            eq_(s.angles.N, 4);
            eq_(s.angles.types, snap0.angles.types);
            numpy.testing.assert_array_equal(s.angles.typeid, numpy.array([0,0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.angles.group, numpy.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0]], dtype=numpy.uint32));

            eq_(s.dihedrals.N, 5);
            eq_(s.dihedrals.types, snap0.dihedrals.types);
            numpy.testing.assert_array_equal(s.dihedrals.typeid, numpy.array([0,0,0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.dihedrals.group, numpy.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=numpy.uint32));

            eq_(s.impropers.N, 6);
            eq_(s.impropers.types, snap0.impropers.types);
            numpy.testing.assert_array_equal(s.impropers.typeid, numpy.array([0,0,0,0,0,0], dtype=numpy.uint32));
            numpy.testing.assert_array_equal(s.impropers.group, numpy.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]], dtype=numpy.uint32));

def test_fallback2():
    with tempfile.TemporaryDirectory() as d:
        snap0 = gsd.hoomd.Snapshot();
        snap0.configuration.step = 1;
        snap0.configuration.dimensions = 3;
        snap0.particles.N = 2;
        snap0.particles.mass = [2,3];

        snap1 = gsd.hoomd.Snapshot();
        snap1.configuration.step = 2;
        snap1.particles.N = 2;
        snap1.particles.position = [[1,2,3],[4,5,6]];

        gsd.hoomd.create(name=d+"/test_fallback2.gsd");

        with gsd.fl.GSDFile(name=d+"/test_fallback2.gsd", mode='w') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            hf.extend([snap0, snap1]);

        with gsd.fl.GSDFile(name=d+"/test_fallback2.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            eq_(len(hf), 2);

            s = hf.read_frame(1);
            numpy.testing.assert_array_equal(s.particles.mass, snap0.particles.mass);

def test_iteration():
    with tempfile.TemporaryDirectory() as d:
        gsd.hoomd.create(name=d+"/test_iteration.gsd");

        with gsd.fl.GSDFile(name=d+"/test_iteration.gsd", mode='w') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            hf.extend((create_frame(i) for i in range(20)));

        with gsd.fl.GSDFile(name=d+"/test_iteration.gsd", mode='r') as f:
            hf = gsd.hoomd.HOOMDTrajectory(f);
            step = hf[-1].configuration.step;
            eq_(step, 20);

            step = hf[-2].configuration.step;
            eq_(step, 19);

            step = hf[-3].configuration.step;
            eq_(step, 18);

            step = hf[0].configuration.step;
            eq_(step, 1);

            snaps = hf[5:10];
            steps = [snap.configuration.step for snap in snaps];
            eq_(steps, [6,7,8,9,10]);

            snaps = hf[15:50];
            steps = [snap.configuration.step for snap in snaps];
            eq_(steps, [16,17,18,19,20]);

            snaps = hf[15:-3];
            steps = [snap.configuration.step for snap in snaps];
            eq_(steps, [16,17]);
