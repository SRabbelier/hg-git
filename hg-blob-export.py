#!/usr/bin/env python

import binascii
import sys

from mercurial import repo,hg,cmdutil,util,ui,revlog,node

LF = '\n'
SP = ' '
NEXT_ID = 0

def curid():
  return NEXT_ID

def nextid():
  global NEXT_ID
  NEXT_ID += 1
  return NEXT_ID

def tohex(binhex):
  return binascii.hexlify(binhex)

def write(*args):
  msg = ''.join([str(i) for i in args])
  sys.stdout.write(msg)

def write_data(data):
  count = len(data)
  write('data', SP, count, LF)
  write(data, LF)

def write_mark(idnum):
  write('mark', SP, ':', idnum, LF)

def write_blob(data, idnum):
  write('blob', LF)
  write_mark(idnum)
  write_data(data)

def export_file(ctx, file):
  fctx = ctx.filectx(file)
  data = fctx.data()

  idnum = nextid()

  write_blob(data, idnum)

  return idnum

def export_files(ctx, manifest, mapping):
  updates = {}

  for name in ctx.files():
    # file got deleted
    if name not in manifest:
      continue

    nodesha = manifest[name]
    hash = tohex(nodesha)

    if hash in mapping:
      continue

    mapping[hash] = export_file(ctx, name)

  return updates

def export_revision(repo, revnum, mapping):
  ctx = repo.changectx(revnum)
  manifest = ctx.manifest()

  sys.stderr.write("Exporting revision %d.\n" % revnum)

  export_files(ctx, manifest, mapping)

def write_marks(mapping):
  f = open('hg.marks', 'w')

  second = lambda (a, b): b

  for hash, mark in sorted(mapping.iteritems(), key=second):
    f.write(':%d %s\n' % (mark, hash))

  f.close()

def read_marks():
  f = open('hg.marks')

  marks = [i.strip().split(' ') for i in f.readlines()]
  mapping = dict((i[1], int(i[0][1:])) for i in marks)

  return mapping

def export_range(repo, end, mapping):
  for i in range(end):
    export_revision(repo, i, mapping)


def export_repo(repopath, end, resume):
  sys.stderr.write("Exporting '%s' up to %d\n" % (repopath, end))

  myui = ui.ui()
  myui.setconfig('ui', 'interactive', 'off')
  repo = hg.repository(myui, repopath)

  mapping = {}

  if resume:
    mapping = read_marks()

  if not end:
    end = len(repo.changelog)

  try:
    export_range(repo, end, mapping)
  except KeyboardInterrupt, e:
    sys.stderr.write("\nInterrupted.")

  write_marks(mapping)

  sys.stderr.write("Done!\n")

def main(argv):
  repopath = argv[0]
  end = int(argv[1]) if len(argv) > 1 else 0
  resume = len(argv) > 2

  export_repo(repopath, end, resume)

if __name__ == '__main__':
  argv = sys.argv

  if len(argv) < 2:
    sys.stderr.write("syntax: %s <repopath> [<end> [-r|--resume]]\n" % argv[0])
    sys.stderr.write("  repopath: any string that hg accepts as a repo\n")
    sys.stderr.write("  end: an integer indicating the last hg revision\n")
    sys.stderr.write("  resume: whether to resume from a previous export\n")
    sys.exit(255)
  else:
    main(argv[1:])
