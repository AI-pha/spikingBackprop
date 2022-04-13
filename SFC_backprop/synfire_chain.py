#!/usr/bin/env python# -*- coding: utf-8 -*-import numpy as npimport scipy.sparse as sparseclass ConnectedGroups:    """    Flexible class that gets string based definitions of neuron groups and connections (between layers)    as input and creates the net    """    def __init__(self, net, topology, params, verbose=True):        self.net = net        # self.layer_maps = {}        self.loihi_groups = {}        self.loihi_connections = {}        self.loihi_reinf_connections = {}        self.spikeprobes = {}        self.connection_types = params['connection_types']        self.neuron_types = params['neuron_types']        self.layers = topology['layers']        self.connected_pairs = topology['connected_pairs']        self.num_populations = params['num_populations']        self.params = params        self.verbose = verbose        for gr_name, gr_type in self.layers.items():            neuron_type = gr_type[1]            N = self.num_populations[gr_type[0]]            self._init_group(gr_name, neuron_type, N)        for conn_pair in self.connected_pairs:            self._init_connection(conn_pair)        self.num_gate = params['num_gate']    def _init_group(self, gr_name, neuron_type, N):        if self.verbose:            print(gr_name)        neuron_params = self.params['neuron_types'][neuron_type]        neuron_creator = neuron_params['neuron_creator']        self.loihi_groups[gr_name] = neuron_creator(self.net, N, parameters=neuron_params, name=gr_name,                                                    verbose=self.verbose)    def _init_connection(self, conn_pair):        pre_layer = conn_pair[0]        post_layer = conn_pair[1]        conn_type = conn_pair[2]        pre_layer_type = self.layers[pre_layer][0]        pre_neuron_type = self.layers[pre_layer][1]        # pre_neuron_params = self.neuron_types[pre_neuron_type]        num_pop_pre = self.num_populations[pre_layer_type]        post_layer_type = self.layers[post_layer][0]        post_neuron_type = self.layers[post_layer][1]        # post_neuron_params = self.neuron_types[post_neuron_type]        num_pop_post = self.num_populations[post_layer_type]        conn_parameters = self.connection_types[conn_type]['params']        synapse_creator = self.connection_types[conn_type]['syn']        if self.verbose:            print('connecting ', pre_layer + ' to ' + post_layer + ' with type ' + conn_type)        syn_name_full = 's_' + pre_layer + '_' + post_layer + '_' + conn_type        pop_conn_type = self.connection_types[conn_type]['pop_conn_type']        if pop_conn_type == '1:1':            assert num_pop_pre == num_pop_post            conn_mask = sparse.eye(num_pop_pre)  # sparse.eye(num_pop_pre)        elif pop_conn_type == 'a:a':            conn_mask = None  # np.ones((num_pop_post,num_pop_pre))        elif pop_conn_type == '1:a':            assert num_pop_pre == 1            conn_mask = None        else:            raise ValueError('unknown pop_conn_type in ' + str(syn_name_full) + ': ' + str(pop_conn_type))        # create actual loihi synapse        self.loihi_connections[syn_name_full] = synapse_creator(self.net, self.loihi_groups[pre_layer],                                                                self.loihi_groups[post_layer],                                                                conn_parameters=conn_parameters,                                                                mask=conn_mask, name=syn_name_full,                                                                verbose=self.verbose)    def get_activity(self, layer, phase, population=None):        return self.activity_in_gating_window(layer_name=layer, phase=phase, population=population)    def activity_in_gating_window(self, layer_name, phase, population=None):        all_spikes = self.spikeprobes[layer_name].data.T[self.num_gate:]        act_phase = all_spikes[np.arange(phase, all_spikes.shape[0], self.num_gate)]        # plt.figure()        # plt.imshow(act_phase[:,15].reshape(10,10))        if population is not None:            act_phase = act_phase[population]        return act_phase    def get_potential(self, layer_name, phase, population=None):        all_v = self.vprobes[layer_name].data.T[self.num_gate:]        v_phase = all_v[np.arange(phase, all_v.shape[0], self.num_gate)]        # plt.figure()        # plt.imshow(act_phase[:,15].reshape(10,10))        if population is not None:            v_phase = v_phase[:, population]        return v_phase / 64