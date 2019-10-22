def stack(self, group='all', type='linear', npts_tol=0):
	"""
	Return stream with traces stacked by the same selected metadata.

	:param str group: Stack waveforms together which have the same metadata
		given by this parameter. The parameter should name the
		corresponding keys of the stats object,
		e.g. ``'{network}.{station}'`` for stacking all
		locations and channels of the stations and returning a stream
		consisting of one stacked trace for each station.
		This parameter can take two special values,
		``'id'`` which stacks the waveforms by SEED id and
		``'all'`` (default) which stacks together all traces in the stream.
	:type type: str or tuple
	:param type: Type of stack, one of the following:
		``'linear'``: average stack (default),
		``('pw', order)``: phase weighted stack of given order,
		see [Schimmel1997]_,
		``('root', order)``: root stack of given order.
	:param int npts_tol: Tolerate traces with different number of points
		with a difference up to this value. Surplus samples are discarded.

	:returns: New stream object with stacked traces. The metadata of each
		trace (inlcuding starttime) corresponds to the metadata of the
		original traces if those are the same. Additionaly, the entries
		``stack`` (result of the format operation on the group parameter)
		and ``stack_count`` (number of stacked traces)
		are written to the stats object(s).

	>>> from obspy import read
	>>> st = read()
	>>> stack = st.stack()
	>>> print(stack)  # doctest: +ELLIPSIS
	1 Trace(s) in Stream:
	BW.RJOB.. | 2009-08-24T00:20:03.000000Z - ... | 100.0 Hz, 3000 samples
	"""
	import collections
	import numpy as np
	
	if group == 'id':
		group = '{network}.{station}.{location}.{channel}'
	groups = collections.defaultdict(list)
	for tr in self:
		groups[group.format(**tr.stats)].append(tr)
	stacks = []
	for groupid, traces in groups.items():
		header = {k: v for k, v in traces[0].stats.items()
				  if all(tr.stats.get(k) == v for tr in traces)}
		header['stack'] = groupid
		header['stack_count'] = len(traces)
		npts_all = [len(tr) for tr in traces]
		npts_dif = np.ptp(npts_all)
		npts = min(npts_all)
		if npts_dif > npts_tol:
			msg = ('Difference of number of points of the traces is higher'
				   ' than requested tolerance ({} > {})')
			raise ValueError(msg.format(npts_dif, npts_tol))
		data = np.array([tr.data[:npts] for tr in traces])
		if type == 'linear':
			stack = np.mean(data, axis=0)
		elif type[0] == 'pw':
			from scipy.signal import hilbert
			from scipy.fftpack import next_fast_len
			nfft = next_fast_len(npts)
			anal_sig = hilbert(data, N=nfft)[:, :npts]
			norm_anal_sig = anal_sig / np.abs(anal_sig)
			phase_stack = np.abs(np.mean(norm_anal_sig, axis=0)) ** type[1]
			stack = np.mean(data, axis=0) * phase_stack
		elif type[0] == 'root':
			r = np.mean(np.sign(data) * np.abs(data)
						** (1 / type[1]), axis=0)
			stack = np.sign(r) * np.abs(r) ** type[1]
		else:
			raise ValueError('stack type is not valid.')
		stacks.append(traces[0].__class__(data=stack, header=header))
	return self.__class__(stacks)
