#!/usr/bin/env python3
# Copyright 2023 ETH Zurich and University of Bologna.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
#
# Luca Colagrande <colluca@iis.ee.ethz.ch>

import sys
import torch
from pathlib import Path
from datagen import golden_model

sys.path.append(str(Path(__file__).parent / '../../../../util/sim/'))
from verif_utils import Verifier  # noqa: E402
from data_utils import ctype_from_precision_t  # noqa: E402


class LayernormVerifier(Verifier):

    OUTPUT_UIDS = ['ofmap']

    def __init__(self):
        super().__init__()
        self.layer_struct = {
            'batch_size': 'I',
            'seq_len': 'I',
            'embeddings': 'I',
            'n_tiles': 'I',
            'baseline': 'I',
            'eps': 'f',
            'ifmap_ptr': 'I',
            'ofmap_ptr': 'I',
            'dtype': 'I'
        }
        self.layer = self.get_input_from_symbol('layer', self.layer_struct)
        self.batch_size = self.layer['batch_size']
        self.seq_len = self.layer['seq_len']
        self.embeddings = self.layer['embeddings']
        self.eps = self.layer['eps']
        self.prec = self.layer['dtype']

    def get_actual_results(self):
        return self.get_output_from_symbol('ofmap', ctype_from_precision_t(self.prec))

    def get_expected_results(self):
        ifmap = self.get_input_from_symbol('ifmap', ctype_from_precision_t(self.prec))
        ifmap = ifmap.reshape(self.batch_size, self.seq_len, self.embeddings)
        ifmap = torch.from_numpy(ifmap)
        return golden_model(ifmap, self.eps, self.embeddings, self.prec).detach().numpy().flatten()

    def check_results(self, *args):
        return super().check_results(*args, atol=0.001)


if __name__ == "__main__":
    sys.exit(LayernormVerifier().main())
