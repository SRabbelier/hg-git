#!/usr/bin/env python

def parse(name):
  try:
    f = open(name)
    lines = f.readlines()
    f.close()
    parsed = [i.strip().split(' ') for i in lines]
    return dict((i[0], i[1]) for i in parsed)
  except IOError:
    return {}

def main():
  hg = parse('hg.marks')
  git = parse('git.marks')
  git_hg = open('git-hg.marks', 'w')

  for mark, hghash in hg.iteritems():
    if mark not in git:
      continue

    githash = git[mark]

    git_hg.write('%s %s\n' % (githash, hghash))

  git_hg.close()

if __name__ == '__main__':
  main()
