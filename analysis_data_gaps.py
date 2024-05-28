# Анализ пропусков данных

import pandas as pd

def analysis_data_gaps(all_data, search_data, index, value_max):
  indexes = search_data.loc[search_data[index] > value_max].index

  dst = all_data[0].loc[indexes, 'dst']
  ae = all_data[0].loc[indexes, 'ae']
  al = all_data[0].loc[indexes, 'al']
  bx = all_data[0].loc[indexes, 'bx']
  by = all_data[0].loc[indexes, 'by']
  bz = all_data[0].loc[indexes, 'bz']
  vsw = all_data[0].loc[indexes, 'vsw']
  dsw = all_data[0].loc[indexes, 'dsw']
  tsw = all_data[0].loc[indexes, 'tsw']
  kp = all_data[1].loc[indexes, 'kp']
  ap = all_data[1].loc[indexes, 'ap']
  f107 = all_data[2].loc[indexes, 'f107']

  result = pd.DataFrame({'dst': dst})
  result['ae'] = ae
  result['al'] = al
  result['bx'] = bx
  result['by'] = by
  result['bz'] = bz
  result['vsw'] = vsw
  result['dsw'] = dsw
  result['tsw'] = tsw
  result['kp'] = kp
  result['ap'] = ap
  result['f107'] = f107

  min_values = result.min().to_frame().T
  min_values.index = ['min_values']
  max_values = result.max().to_frame().T
  max_values.index = ['max_values']
  # std_values = result.std().to_frame().T
  # std_values.index = ['std_values']

  result = pd.concat([result, min_values, max_values])

  return result