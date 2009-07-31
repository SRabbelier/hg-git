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
    if name == ".hgtags":
      continue

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

  export_files(ctx, manifest, mapping)

def export_repo(repopath, start, end):
  sys.stderr.write("Exporting '%s' from %d up to %d\n" % (repopath, start, end))

  myui = ui.ui()
  myui.setconfig('ui', 'interactive', 'off')
  repo = hg.repository(myui, repopath)

  mapping = {}

  if not end:
    end = len(repo.changelog)

  for i in range(end):
    export_revision(repo, i, mapping)

  f = open('hg.marks', 'w')
  second = lambda (a, b): b
  for hash, mark in sorted(mapping.iteritems(), key=second):
    f.write(':%d %s\n' % (mark, hash))
  f.close()

  sys.stderr.write("Done!\n")

def main(argv):
  repopath = argv[0]
  end = int(argv[1]) if len(argv) > 1 else 0
  start = int(argv[2]) if len(argv) > 2 else 0

  export_repo(repopath, start, end)

if __name__ == '__main__':
  argv = sys.argv

  if len(argv) < 2:
    sys.stderr.write("syntax: %s <repopath> [<end> [<start>]]\n" % argv[0])
    sys.stderr.write("  repopath: any string that hg accepts as a repo\n")
    sys.stderr.write("  end: an integer indicating the last hg revision\n")
    sys.stderr.write("  start: an integer indicating the first hg revision\n")
    sys.exit(255)
  else:
    main(argv[1:])
