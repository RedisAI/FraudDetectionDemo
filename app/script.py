# Create 256-values reference tensor for the credit-fraud inference model.
def create_ref_tensor(tensors: List[Tensor]):
    size = (1, 256)
    # No input
    if len(tensors) == 0:
        return torch.zeros(size)

    # Concat tensors
    c = torch.cat(tensors).reshape((1, -1))
    s = c.size()
    if s == size:
        return c
    elif s[1] < size[1]:
        # Not enough data - pad with zeros
        res = torch.zeros(size)
        res[0, :s[1]] = c.squeeze()
        return res
    else:
        # Too much data - trim
        return c[0, :size[1]].unsqueeze(0)


def hashes_to_tensor(tensors: List[Tensor], keys: List[str], args: List[str]):

    # Get the hashes from redis
    tensors = []
    for key in keys:
        hash_values = redis.asList(redis.execute("HVALS", key))
        # convert every value in the hash to a torch tensor, and concatenate them to a single tensor
        tensor = [torch.tensor(float(str(v))).reshape(1, 1) for v in hash_values]
        tensors.append(torch.cat(tensor, dim=0))

    return create_ref_tensor(tensors)


# Average the two input tensors
def post_processing(tensors: List[Tensor], keys: List[str], args: List[str]):
    return (tensors[0]+tensors[1]) / 2.0
