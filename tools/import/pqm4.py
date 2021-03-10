#!/usr/bin/env python3
# -*- coding: utf8 -*-
import csv
import os
import re
import yaml # on Debian/Ubuntu, install the `python3-yaml` package
from collections import Counter, defaultdict, OrderedDict

import inspect
if 'sort_keys' in inspect.signature(yaml.Dumper).parameters.keys():
    yaml_dump = yaml.dump
else:
    print("Your pyYAML version is old. .yaml files will be sorted. Try to use a newer version, if possible.")
    def yaml_dump(data, f, *args, **kwargs):
        kwargs.pop('sort_keys')
        return yaml.dump(data, f, *args, **kwargs)

ENC = 'Key Encapsulation Schemes'
SIG = 'Signature Schemes'
_firstlinemarker = '# generated by pqm4 import script. do not alter this line!'
_schemename_replace = re.compile('^([-A-Za-z0-9]+) \(([\d]+) executions\)$')

# format is: pqm4-name pqdb-scheme pqdb-flavor pqdb-paramset
# to create a list, run this from `/encryption` or `/signatures`:
# printf '%s\n' */*/param/*.yaml | sed 's|param/||; s|\.yaml$||; y|/| |' | column -t
_scheme_to_paramset = '''
    bikel1              bike              bike                  level-1
    firesaber           saber             saberkem-sha3         firesaber
    frodokem640aes      frodo             frodokem-aes          640
    frodokem640shake    frodo             frodokem-shake        640
    kyber1024           kyber             ccakem                1024
    kyber1024-90s       kyber             ccakem-90s            1024
    kyber512            kyber             ccakem                512
    kyber512-90s        kyber             ccakem-90s            512
    kyber768            kyber             ccakem                768
    kyber768-90s        kyber             ccakem-90s            768
    lightsaber          saber             saberkem-sha3         lightsaber
    ntruhps2048509      ntru              ntru-kem              ntruhps2048509
    ntruhps2048677      ntru              ntru-kem              ntruhps2048677
    ntruhps4096821      ntru              ntru-kem              ntruhps4096821
    ntruhrss701         ntru              ntru-kem              ntruhrss701
    ntrulpr761          ntru-prime        lprime                ntrulpr761
    saber               saber             saberkem-sha3         saber
    sikep434            sike              sike-shake256         p434
    sikep503            sike              sike-shake256         p503
    sikep610            sike              sike-shake256         p610
    sikep751            sike              sike-shake256         p751
    sntrup761           ntru-prime        streamlined           sntrup761

    dilithium2                   dilithium  dilithium-shake  medium
    dilithium3                   dilithium  dilithium-shake  recommended
    dilithium4                   dilithium  dilithium-shake  very-high
    falcon-1024                  falcon     falcon           1024
    falcon-512                   falcon     falcon           512
    falcon-512-tree
    luov-47-42-182-chacha        luov       luov-chacha8      luov-47-42-182
    luov-47-42-182-keccak        luov       luov-keccak       luov-47-42-182
    luov-61-60-261-chacha        luov       luov-chacha8      luov-61-60-261
    luov-61-60-261-keccak        luov       luov-keccak       luov-61-60-261
    luov-7-57-197-chacha         luov       luov-chacha8      luov-7-57-197
    luov-7-57-197-keccak         luov       luov-keccak       luov-7-57-197
    sphincs-haraka-128f-robust   sphincs+   sphincs-haraka    128f-robust
    sphincs-haraka-128f-simple   sphincs+   sphincs-haraka    128f-simple
    sphincs-haraka-128s-robust   sphincs+   sphincs-haraka    128s-robust
    sphincs-haraka-128s-simple   sphincs+   sphincs-haraka    128s-simple
    sphincs-haraka-192f-robust   sphincs+   sphincs-haraka    192f-robust
    sphincs-haraka-192f-simple   sphincs+   sphincs-haraka    192f-simple
    sphincs-haraka-192s-robust   sphincs+   sphincs-haraka    192s-robust
    sphincs-haraka-192s-simple   sphincs+   sphincs-haraka    192s-simple
    sphincs-haraka-256f-robust   sphincs+   sphincs-haraka    256f-robust
    sphincs-haraka-256f-simple   sphincs+   sphincs-haraka    256f-simple
    sphincs-haraka-256s-robust   sphincs+   sphincs-haraka    256s-robust
    sphincs-haraka-256s-simple   sphincs+   sphincs-haraka    256s-simple
    sphincs-sha256-128f-robust   sphincs+   sphincs-sha-256   128f-robust
    sphincs-sha256-128f-simple   sphincs+   sphincs-sha-256   128f-simple
    sphincs-sha256-128s-robust   sphincs+   sphincs-sha-256   128s-robust
    sphincs-sha256-128s-simple   sphincs+   sphincs-sha-256   128s-simple
    sphincs-sha256-192f-robust   sphincs+   sphincs-sha-256   192f-robust
    sphincs-sha256-192f-simple   sphincs+   sphincs-sha-256   192f-simple
    sphincs-sha256-192s-robust   sphincs+   sphincs-sha-256   192s-robust
    sphincs-sha256-192s-simple   sphincs+   sphincs-sha-256   192s-simple
    sphincs-sha256-256f-robust   sphincs+   sphincs-sha-256   256f-robust
    sphincs-sha256-256f-simple   sphincs+   sphincs-sha-256   256f-simple
    sphincs-sha256-256s-robust   sphincs+   sphincs-sha-256   256s-robust
    sphincs-sha256-256s-simple   sphincs+   sphincs-sha-256   256s-simple
    sphincs-shake256-128f-robust sphincs+   sphincs-shake256  128f-robust
    sphincs-shake256-128f-simple sphincs+   sphincs-shake256  128f-simple
    sphincs-shake256-128s-robust sphincs+   sphincs-shake256  128s-robust
    sphincs-shake256-128s-simple sphincs+   sphincs-shake256  128s-simple
    sphincs-shake256-192f-robust sphincs+   sphincs-shake256  192f-robust
    sphincs-shake256-192f-simple sphincs+   sphincs-shake256  192f-simple
    sphincs-shake256-192s-robust sphincs+   sphincs-shake256  192s-robust
    sphincs-shake256-192s-simple sphincs+   sphincs-shake256  192s-simple
    sphincs-shake256-256f-robust sphincs+   sphincs-shake256  256f-robust
    sphincs-shake256-256f-simple sphincs+   sphincs-shake256  256f-simple
    sphincs-shake256-256s-robust sphincs+   sphincs-shake256  256s-robust
    sphincs-shake256-256s-simple sphincs+   sphincs-shake256  256s-simple
'''
scheme_to_paramset = dict(
        (l.strip().split(' ')[0], re.split(' +', l.strip())[1:] or None)
        for l in _scheme_to_paramset.strip().split('\n'))


def dump_preparsed(csvdata):
    cats = preparse(csvdata)
    for cat, types in cats.items():
        for type, data in types.items():
            print(cat, '/', type)
            for v in data:
                print(v)
            print()

def preparse(csvdata):
    raw = defaultdict(list)
    h1 = h2 = None
    lastwashead = False
    for l in csvdata.splitlines(True):
        if l.rstrip().endswith(',,,,,,,,,,'):
            if lastwashead:
                h1 = h2
            h2 = l.split(',')[0]
            lastwashead = True
        else:
            assert h2 in (ENC, SIG)
            lastwashead = False
            raw[h1, h2].append(l)

    out = defaultdict(lambda: defaultdict(dict))
    for (cat, type) in raw:
        reader = csv.DictReader(raw[cat, type])
        for data in reader:
            if cat == 'Speed Evaluation':
                # replace "schemename (x evaluations)" by two fields
                data = list(data.items())
                k, v = data.pop(0)
                assert k == 'Scheme', "should be 'Scheme': {!r}".format(k)
                m = _schemename_replace.match(v)
                if m is None:
                    raise ValueError("didn't match expected format: {!r}".format(v))
                data.insert(0, ['Number of Executions', m.group(2)])
                #data.insert(0, ['Scheme', m.group(1)])
                scheme = m.group(1)
                data = dict(data)
            else:
                # we don't need an OrderedDict
                # (normal dict also preserves order starting in py3.7)
                data = dict(data)
                scheme = data.pop('Scheme')
            impl = data.pop('Implementation')

            out[cat][type][scheme, impl] = data

    return out


def import_benchmarks(csvdata, type, source):
    assert type in (ENC, SIG)
    data = preparse(csvdata)
    speed = data['Speed Evaluation'][type]
    mem = data['Memory Evaluation'][type]
    skipcounter = Counter()

    for name, impl in sorted(speed.keys() | mem.keys()):

        if not impl.startswith('m4'):
            skipcounter.update((impl,))
            continue
        if scheme_to_paramset.get(name) is None:
            print('{}: Skipping: no mapping defined'.format(name))
            continue

        s, f, p = scheme_to_paramset[name]
        bpath = get_bench_path(type, s, f, 'pq{}-{}'.format(impl, name),
                               p, impl)
        ipath = get_impl_path(type, s, f, 'pq{}-{}'.format(impl, name))
        overwrite = False
        if os.path.exists(bpath):
            with open(bpath) as f:
                if f.readline().strip() != _firstlinemarker:
                    print('{}: Warning: File already exists (and not created '
                          'by us), skipping: {}'.format(name, bpath))
                    continue
                else:
                    overwrite = True
        if os.path.exists(ipath):
            with open(ipath) as f:
                if f.readline().strip() != _firstlinemarker:
                    print('{}: Warning: File already exists (and not created '
                          'by us), skipping: {}'.format(name, ipath))
                    continue
                else:
                    overwrite = True

        timings = getcolumns(speed, type, 'speed', name, impl)
        if not timings:
            print('{}: info: No timing information available'.format(name))
        else:
            timings['unit'] = 'cycles'

        memoryreq = getcolumns(mem, type, 'mem', name, impl)
        if not timings:
            print('{}: info: No memory information available'.format(name))

        data = {
            'links': ['https://github.com/mupq/pqm4/#benchmarks'],
            'sources': [source],
            'platform': 'M4, at 24MHz, using arm-none-eabi-gcc 10.1.0',
        }
        if timings:
            data['timings'] = timings
        if memoryreq:
            data['memory requirements'] = memoryreq

        with open(bpath, 'w') as f:
            f.write(_firstlinemarker + '\n')
            yaml_dump(data, f, sort_keys=False)
            print('{}: bench data written to {}'.format(name, bpath))

        idata = {
            'name': '{} for {} from pqm4'.format(impl, name),
            'links': ['https://github.com/mupq/pqm4/tree/master/{}/{}/{}'
                .format(type2api(type), name, impl)],
            'platform': 'm4',
            'type': 'optimized',
        }
        if impl == 'm4f':
            idata.setdefault('hardware features', []).append('FPU')

        with open(ipath, 'w') as f:
            f.write(_firstlinemarker + '\n')
            yaml_dump(idata, f, sort_keys=False)
            print('{}: impl data written to {}'.format(name, ipath))

    print('Additionally, these implementations were skipped:', dict(skipcounter))


def getcolumns(data, type, cat, name, impl):
    if (name, impl) not in data:
        return {}

    key_mapping = {
        (ENC, 'speed'): [
            ('Key Generation [cycles] (mean)', 'gen'),
            ('Encapsulation [cycles] (mean)', 'enc|sign'),
            ('Decapsulation [cycles] (mean)', 'dec|vrfy')],
        (SIG, 'speed'): [
            ('Key Generation [cycles] (mean)', 'gen'),
            ('Sign [cycles] (mean)', 'enc|sign'),
            ('Verify [cycles] (mean)', 'dec|vrfy')],
        (ENC, 'mem'): [
            ('Key Generation [bytes]', 'gen'),
            ('Encapsulation [bytes]', 'enc|sign'),
            ('Decapsulation [bytes]', 'dec|vrfy')],
        (SIG, 'mem'): [
            ('Key Generation [bytes]', 'gen'),
            ('Sign [bytes]', 'enc|sign'),
            ('Verify [bytes]', 'dec|vrfy')],
    }

    return dict((yamlkey, int(data[name, impl][datakey]))
            for datakey, yamlkey in key_mapping[type, cat])


def type2path(type):
    if type == ENC:
        return 'encryption'
    if type == SIG:
        return 'signatures'
    return type

def type2api(type):
    if type == ENC:
        return 'crypto_kem'
    if type == SIG:
        return 'crypto_sig'
    raise ValueError('Must be ENC or SIG')

def get_paramset_path(type, scheme, flavor, paramset):
    return os.path.join(type2path(type), scheme, flavor, 'param', paramset + '.yaml')

def get_impl_path(type, scheme, flavor, impl):
    return os.path.join(type2path(type), scheme, flavor, 'impl', impl + '.yaml')

def get_bench_path(type, scheme, flavor, impl, paramset, arch):
    return os.path.join(type2path(type), scheme, flavor, 'bench',
            '{}_{}_{}.yaml'.format(impl, paramset, arch))

if __name__ == '__main__':
    import sys
    PQM4_JSON = 'https://api.github.com/repos/mupq/pqm4/commits?path=benchmarks.csv&sha=master'
    PQM4_CSV_BASE = 'https://raw.githubusercontent.com/mupq/pqm4/{}/benchmarks.csv'
    PQM4_SOURCE_URL_BASE = 'https://github.com/mupq/pqm4/blob/{}/benchmarks.csv'

    if len(sys.argv) > 2:
        # only use this for developing
        with open(sys.argv[1], newline='') as f:
            print('Using', sys.argv[1])
            d = f.read()
            sha = sys.argv[2]

    elif len(sys.argv) > 1:
        sys.exit("Error: Please either supply \n"
                 "- no arguments at all (for automatic download), or\n"
                 "- csv file and sha hash of the last commit (for developing)")
        sys.exit(1)

    else:
        import requests # on Debian/Ubuntu, install the `python3-requests` package
        print('Downloading data...')
        r = requests.get(PQM4_JSON)
        assert r.status_code == 200
        sha = r.json()[0]['sha'][:7]
        f = requests.get(PQM4_CSV_BASE.format(sha))
        print('Using', f.request.url)
        assert r.status_code == 200
        d = f.text

    source = PQM4_SOURCE_URL_BASE.format(sha)

    print('\nIMPORTING ENCRYPTION SCHEMES')
    import_benchmarks(d, ENC, source)
    print('\nIMPORTING SIGNATURE SCHEMES')
    import_benchmarks(d, SIG, source)
