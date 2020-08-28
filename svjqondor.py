# -*- coding: utf-8 -*-
import os.path as osp
import logging, subprocess, os, glob, shutil
import qondor, seutils

logger = qondor.setup_logger('svjqondor')

# __________________________________________

MG_TARBALL_PATH = 'root://cmseos.fnal.gov//store/user/klijnsma/semivis/tarballsv2'

def debug(flag=True):
    """Sets the logger level to debug (for True) or warning (for False)"""
    logger.setLevel(logging.DEBUG if flag else logging.WARNING)

def get_mg_tarball_name(mz, rinv, boost=0., **kwargs):
    return (
        'step0_GRIDPACK_s-channel_mMed-{mz:.0f}_mDark-20_rinv-{rinv}_'
        'alpha-peak{boost}_13TeV-madgraphMLM-pythia8.tar.xz'
        .format(
            mz = mz, rinv = rinv,
            boost = '_HT{0:.0f}'.format(boost) if boost > 0. else ''
            )
        )

def download_mg_tarball(mz, rinv, boost=0., dst=None, **kwargs):
    dst = osp.join(
        os.getcwd() if dst is None else dst,
        get_mg_tarball_name(mz, rinv, boost=boost)
        )
    # Tarballs on SE will not have the boost tag but it's irrelevant for mg tarballs, so just set boost to 0
    src = osp.join(MG_TARBALL_PATH, get_mg_tarball_name(mz, rinv, boost=0.))
    if osp.isfile(dst):
        logger.info('File %s already exists', dst)
    else:
        logger.info('Downloading %s --> %s', src, dst)
        seutils.cp(src, dst)

def formatted_filename(pre, mz, rinv, mdark, max_events=None, part=1, boost=400., **kwargs):
    return (
        '{pre}_s-channel'
        '_mMed-{mz:.0f}_mDark-{mdark:.0f}_rinv-{rinv}'
        '_alpha-peak{boost}_13TeV-madgraphMLM-pythia8_{max_events}part-{part}.root'
        .format(
            pre=pre, mz=mz, mdark=mdark, rinv=rinv, part=part,
            max_events='' if max_events is None else 'n-{0}_'.format(max_events),
            boost='_HT{0:.0f}'.format(boost) if boost > 0. else ''
            )
        )

def mg_tarball_cmd(
    year, mz, mdark, rinv,
    boost=None
    ):
    cmd = (
        'python runMG.py'
        ' year={year}'
        ' madgraph=1'
        ' channel=s'
        ' outpre=step0_GRIDPACK'
        ' mMediator={mz:.0f}'
        ' mDark={mdark:.0f}'
        ' rinv={rinv}'
        .format(
            year=year, mz=mz, mdark=mdark, rinv=rinv
            )
        )
    if boost:
        cmd += ' boost={0:.0f}'.format(boost)
    return cmd

# step0_GRIDPACK_s-channel_mMed-250_mDark-20_rinv-0.3_alpha-peak_13TeV-madgraphMLM-pythia8_n-1.tar.xz
def run_mg_tarball_cmd(cmssw, **physics):
    testdir = osp.join(cmssw.cmssw_src, 'SVJ/Production/test')
    expected_outfile = osp.join(
        testdir,
        formatted_filename(pre='step0_GRIDPACK', **physics).replace('.root', '.tar.xz').replace('part', 'n')
        )
    cmssw.run_commands([
        'cd {0}'.format(testdir),
        mg_tarball_cmd(**physics)
        ])
    return expected_outfile

def step_cmd(
    inpre, outpre,
    year, part, mz, mdark, rinv,
    max_events=None, boost=None
    ):
    cmd = (
        'cmsRun runSVJ.py'
        ' year={year}'
        ' madgraph=1'
        ' channel=s'
        ' outpre={outpre}'
        ' config={outpre}'
        ' part={part}'
        ' mMediator={mz:.0f}'
        ' mDark={mdark:.0f}'
        ' rinv={rinv}'
        ' inpre={inpre}'
        .format(
            year=year, inpre=inpre, outpre=outpre,
            mz=mz, mdark=mdark, rinv=rinv, part=part,
            )
        )
    if boost:
        cmd += ' boost={0:.0f}'.format(boost)
    if max_events:
        cmd += ' maxEvents={0}'.format(max_events)
    return cmd


def run_step_cmd(cmssw, inpre, outpre, **physics):
    testdir = osp.join(cmssw.cmssw_src, 'SVJ/Production/test')
    if inpre.startswith('step0'):
        expected_infile = osp.join(testdir, get_mg_tarball_name(**physics))
    else:
        expected_infile = osp.join(testdir, formatted_filename(pre=inpre, **physics))
    expected_outfile = osp.join(testdir, formatted_filename(pre=outpre, **physics))
    if not osp.isfile(expected_infile):
        raise RuntimeError(
            'Expected file {0} to exist by now'
            .format(expected_infile)
            )
    cmssw.run_commands([
        'cd {0}'.format(testdir),
        step_cmd(inpre, outpre, **physics)
        ])
    return expected_outfile




